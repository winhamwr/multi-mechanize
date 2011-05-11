#!/usr/bin/env python
#
#  Copyright (c) 2010 Corey Goldberg (corey@goldb.org)
#  License: GNU LGPLv3 - distributed under the terms of the GNU Lesser General
#  Public License version 3
#
#  This file is part of Multi-Mechanize:
#       Multi-Process, Multi-Threaded, Web Load Generator, with python-mechanize
#       agents
#
#  requires Python 2.6+



import ConfigParser
import glob
import logging
import multiprocessing
import optparse
import os
import Queue
import shutil
import subprocess
import sys
import threading
import time
import lib.results as results
import lib.progressbar as progressbar
import csv
import json

MM_ROOT = os.path.abspath(os.path.dirname(__file__))

usage = 'Usage: %prog <project name> [options]'
parser = optparse.OptionParser(usage=usage)
parser.add_option('-p', '--port',
                  dest='port', type='int',
                  help='rpc listener port')
parser.add_option('-v', '--verbose',
                  dest='verbose', action='store_true', default=False,
                  help='Produce verbose output')
cmd_opts, args = parser.parse_args()

if cmd_opts.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mm')

try:
    project_name = args[0]
except IndexError:
    logger.critical('\nNo project specified\n\n')
    logger.critical('usage: python multi-mechanize.py <project_name>\n')
    logger.critical('example: python multi-mechanize.py default_project\n\n')
    sys.exit(1)

def get_project_path(project_name):
    rel_project_path = os.path.join('projects', project_name)
    abs_project_path = os.path.abspath(project_name)
    mm_root_project_path = os.path.join(MM_ROOT, 'projects', project_name)

    paths = [rel_project_path, abs_project_path, mm_root_project_path]
    for path in paths:
        if os.path.exists(path):
            return path

    logger.critical('\nCan not find project: %s\n\n', project_name)
    logger.debug('Searched paths: %s\n\n', paths)
    sys.exit(1)

project_path = get_project_path(project_name)
logger.debug("Project path is %s", project_path)

def get_mm_templates_dirs(project_path):
    """
    Get a list of filesystem directories Jinja can use to search for templates.

    Uses project-level templates by default and falls back to multi-mechanize
    default templates relative to this file.
    """
    dir_paths = [
        os.path.join(project_path, 'templates'),
        os.path.join(MM_ROOT, 'lib', 'templates'),
    ]
    if not any([os.path.exists(dir_path) for dir_path in dir_paths]):
        logger.critical('\nNo templates directory found')
        logger.debug('Checked: %s\n', dir_paths)

    return dir_paths


def import_test_scripts(project_path):
    scripts_path = os.path.join(project_path, 'test_scripts')
    sys.path.append(scripts_path)

    script_modules = {}
    for f in glob.glob( '%s/*.py' % scripts_path):  # import all test scripts as modules
        logger.debug("Importing script: %s", f)
        script_name = f.replace(scripts_path, '')
        if script_name[0] == os.sep:
            # Strip leading dot
            script_name = script_name[1:]
        script_path = script_name.replace(os.sep, '.').replace('.py', '')
        script_modules[script_name] = __import__(script_path, {}, {}, [''])

    logger.debug("Imported %s test scripts", len(script_modules))
    return script_modules

test_scripts = import_test_scripts(project_path)

def main():
    if cmd_opts.port:
        import lib.rpcserver
        lib.rpcserver.launch_rpc_server(cmd_opts.port, project_name, run_test)
    else:
        run_test(project_name, project_path)



def run_test(project_name, project_path, remote_starter=None):
    if remote_starter is not None:
        remote_starter.test_running = True
        remote_starter.output_dir = None

    run_time, rampup, console_logging, results_ts_interval, user_group_configs, results_database, post_run_script = configure(project_name, project_path)

    run_localtime = time.localtime()
    time_str = time.strftime('%Y.%m.%d_%H.%M.%S', run_localtime)
    output_dir = os.path.join(project_path, 'results', 'results_%s' % time_str)
    logger.debug("Test output directory: %s", output_dir)

    # this queue is shared between all processes/threads
    queue = multiprocessing.Queue()
    rw = ResultsWriter(queue, output_dir, console_logging)
    rw.daemon = True
    rw.start()

    user_groups = []
    for i, ug_config in enumerate(user_group_configs):
        ug = UserGroup(
            queue,
            i,
            ug_config.name,
            ug_config.num_threads,
            test_scripts[ug_config.script_file],
            run_time,
            rampup)
        user_groups.append(ug)
    for user_group in user_groups:
        user_group.start()

    start_time = time.time()

    if console_logging:
        for user_group in user_groups:
            user_group.join()
    else:
        print '\n  user_groups:  %i' % len(user_groups)
        print '  threads: %i\n' % (ug_config.num_threads * len(user_groups))
        p = progressbar.ProgressBar(run_time)
        elapsed = 0
        while elapsed < (run_time + 1):
            p.update_time(elapsed)
            if sys.platform.startswith('win'):
                print '%s   transactions: %i  timers: %i  errors: %i\r' % (p, rw.trans_count, rw.timer_count, rw.error_count),
            else:
                print '%s   transactions: %i  timers: %i  errors: %i' % (p, rw.trans_count, rw.timer_count, rw.error_count)
                sys.stdout.write(chr(27) + '[A' )
            time.sleep(1)
            elapsed = time.time() - start_time

        print p

        while [user_group for user_group in user_groups if user_group.is_alive()] != []:
            if sys.platform.startswith('win'):
                logger.info('waiting for all requests to finish...\r')
            else:
                logger.info('waiting for all requests to finish...\r')
                sys.stdout.write(chr(27) + '[A' )
            time.sleep(.5)

        if not sys.platform.startswith('win'):
            print

    # all agents are done running at this point
    time.sleep(.2) # make sure the writer queue is flushed
    logger.info('\nanalyzing results...\n')
    results.output_results(
        output_dir,
        os.path.join(output_dir, 'results.csv'),
        run_time,
        rampup,
        results_ts_interval,
        user_group_configs,
        template_dirs=get_mm_templates_dirs(project_path),
    )
    logger.info('created: %sresults.html\n', output_dir)

    # copy config file to results directory
    project_config = os.path.join(project_path, 'config.cfg')
    saved_config = os.path.join(output_dir, 'config.cfg')
    shutil.copy(project_config, saved_config)

    if results_database is not None:
        logger.info('loading results into database: %s\n', results_database)
        import lib.resultsloader
        lib.resultsloader.load_results_database(
            project_name,
            run_localtime,
            output_dir,
            results_database,
            run_time,
            rampup,
            results_ts_interval,
            user_group_configs)

    if post_run_script is not None:
        logger.info('running post_run_script: %s\n', post_run_script)
        subprocess.call(post_run_script)

    logger.info('done.')

    if remote_starter is not None:
        remote_starter.test_running = False
        remote_starter.output_dir = output_dir

    return



def configure(project_name, project_path):
    user_group_configs = []
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(project_path, 'config.cfg'))
    for section in config.sections():
        if section == 'global':
            run_time = config.getint(section, 'run_time')
            rampup = config.getint(section, 'rampup')
            console_logging = config.getboolean(section, 'console_logging')
            results_ts_interval = config.getint(section, 'results_ts_interval')
            try:
                results_database = config.get(section, 'results_database')
            except ConfigParser.NoOptionError:
                results_database = None
            try:
                post_run_script = config.get(section, 'post_run_script')
            except ConfigParser.NoOptionError:
                post_run_script = None
        else:
            threads = config.getint(section, 'threads')
            script = config.get(section, 'script')
            user_group_name = section
            ug_config = UserGroupConfig(threads, user_group_name, script)
            user_group_configs.append(ug_config)

    return (run_time, rampup, console_logging, results_ts_interval, user_group_configs, results_database, post_run_script)



class UserGroupConfig(object):
    def __init__(self, num_threads, name, script_file):
        self.num_threads = num_threads
        self.name = name
        self.script_file = script_file



class UserGroup(multiprocessing.Process):
    def __init__(
        self, queue, process_num, user_group_name, num_threads, script_module, run_time, rampup):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.process_num = process_num
        self.user_group_name = user_group_name
        self.num_threads = num_threads
        self.script_module = script_module
        self.run_time = run_time
        self.rampup = rampup
        self.start_time = time.time()

    def run(self):
        threads = []
        for i in range(self.num_threads):
            spacing = float(self.rampup) / float(self.num_threads)
            if i > 0:
                time.sleep(spacing)
            agent_thread = Agent(
                self.queue, self.process_num, i, self.start_time, self.run_time,
                self.user_group_name, self.script_module)
            agent_thread.daemon = True
            threads.append(agent_thread)
            agent_thread.start()
        for agent_thread in threads:
            agent_thread.join()


class Agent(threading.Thread):
    def __init__(
        self, queue, process_num, thread_num, start_time, run_time, user_group_name, script_module):
        threading.Thread.__init__(self)
        self.queue = queue
        self.process_num = process_num
        self.thread_num = thread_num
        self.start_time = start_time
        self.run_time = run_time
        self.user_group_name = user_group_name
        self.script_module = script_module

        # choose most accurate timer to use (time.clock has finer granularity than time.time on windows, but shouldn't be used on other systems)
        if sys.platform.startswith('win'):
            self.default_timer = time.clock
        else:
            self.default_timer = time.time


    def run(self):
        elapsed = 0
        try:
            Transaction = getattr(self.script_module, 'Transaction')
        except NameError, e:
            logger.critical('Can not find Transaction class in test script: %s.', self.script_module)
            logger.critical('Aborting user group: %s\n', self.user_group_name)
            return
        try:
            trans = Transaction()
        except Exception, e:
            logger.critical('Failed initializing Transaction: %s', self.script_module)
            logger.critical('Aborting user group: %s\n', self.user_group_name)
            return
        trans.custom_timers = {}

        # scripts have access to these vars, which can be useful for loading unique data
        trans.thread_num = self.thread_num
        trans.process_num = self.process_num

        while elapsed < self.run_time:
            error = ''
            start = self.default_timer()

            try:
                trans.run()
            except Exception, e:  # test runner catches all script exceptions here
                error = str(e).replace(',', '')

            finish = self.default_timer()

            scriptrun_time = finish - start
            elapsed = time.time() - self.start_time

            epoch = time.mktime(time.localtime())

            fields = (elapsed, epoch, self.user_group_name, scriptrun_time, error, trans.custom_timers)
            self.queue.put(fields)



class ResultsWriter(threading.Thread):
    def __init__(self, queue, output_dir, console_logging):
        threading.Thread.__init__(self)
        self.queue = queue
        self.console_logging = console_logging
        self.output_dir = output_dir
        self.trans_count = 0
        self.timer_count = 0
        self.error_count = 0

        try:
            os.makedirs(self.output_dir, 0755)
        except OSError:
            logger.critical(
                'Can not create output directory %s\n',
                self.output_dir)
            sys.exit(1)

    def run(self):
        with open(os.path.join(self.output_dir, 'results.csv'), 'wb') as filestream:
            f = csv.writer(filestream)
            while True:
                try:
                    elapsed, epoch, self.user_group_name, scriptrun_time, error, custom_timers = self.queue.get(False)
                    self.trans_count += 1
                    self.timer_count += len(custom_timers)
                    if error != '':
                        self.error_count += 1
                    f.writerow((int(self.trans_count), elapsed, epoch, self.user_group_name, scriptrun_time, error, json.dumps(custom_timers)))
                    filestream.flush()
                    if self.console_logging:
                        print '%i, %.3f, %i, %s, %.3f, %s, %s' % (self.trans_count, elapsed, epoch, self.user_group_name, scriptrun_time, error, repr(custom_timers))
                except Queue.Empty:
                    time.sleep(.05)



if __name__ == '__main__':
    main()

