#!/usr/bin/env python

"""
Script to convert the CSV output from a multi-mechanize run in to Jmeter's
XML-based format.

This is useful if you'd like to use Multi-Mechanize with a CI server and take
advantage of an existing JMeter plugin like:
https://wiki.jenkins-ci.org/display/JENKINS/Performance+Plugin
"""
import logging
import os.path
from optparse import OptionParser
from xml.etree import ElementTree as ET

from multi_mechanize.results import Results, ResponseStats

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('mmjm')

def parse_mm_data(csv_path):
    """
    Parse a Multi-Mechanize results CSV file and convert it to a list
    of ``ResponseStats`` objects.
    """
    # TODO: Actually get the run_time configuration value to properly
    # filter out results after the cutoff
    results = Results(csv_path, 100000)
    mm_data = results.parse_file()

    return mm_data

def write_jmeter_output(mm_data, output_path):
    """
    Take the list of ``ResponseStats`` objects and write a JMeter 2.1
    JST-formatted XML file to ``output_path``.

    JMeter JST file documentation:
    http://jakarta.apache.org/jmeter/usermanual/listeners.html
    """
    root = ET.Element('testResults')
    root.set('version', "1.2")

    for test_transaction in mm_data:
        # Each transaction might have multiple timers
        transaction_root = ET.SubElement(root, 'sample')
        # JMeter uses ms for time
        ms_trans_time = test_transaction.trans_time * 1000
        transaction_root.set('t', '%d' % ms_trans_time)
        transaction_root.set('ts', '%d' % test_transaction.epoch_secs) # timestamp
        transaction_root.set('lb', test_transaction.user_group_name) # Label
        transaction_root.set('sc', '1') # Sample count

        if test_transaction.error:
            transaction_root.set('ec', '1') # Was an error
            transaction_root.set('s', 'false') # Was an error
            # Errors don't have custom_timers
            continue
        else:
            transaction_root.set('ec', '0')
            transaction_root.set('s', 'true')

        # Parse the custom_timers and add each as a JMeter sub-sample
        for timer_name, timer_duration in test_transaction.custom_timers.items():
            timer_duration = float(timer_duration)
            timer_element = ET.SubElement(transaction_root, 'sample')
            ms_trans_time = timer_duration * 1000
            timer_element.set('t', '%d' % ms_trans_time)
            timer_element.set('ts', '%d' % test_transaction.epoch_secs)
            timer_element.set('lb', timer_name)
            timer_element.set('sc', '1')
            timer_element.set('ec', '0')
            timer_element.set('s', 'true')

    tree = ET.ElementTree(root)
    tree.write(output_path)

def main():
    parser = OptionParser(
        "usage: %prog <mm_csv_path> <xml_output_path> [options]")

    options, args = parser.parse_args()

    # Validation
    if len(args) != 2:
        parser.error("<mm_csv_path> and <xml_output_path> are required")

    csv_path = args[0]
    output_path = args[1]
    if not os.path.exists(csv_path):
        logger.critical("CSV file does not exist: %s", csv_path)
        exit(1)

    mm_data = parse_mm_data(csv_path)
    write_jmeter_output(mm_data, output_path)
    logger.info("Wrote Jmeter JTL output to: %s", output_path)

if __name__ == '__main__':
    main()