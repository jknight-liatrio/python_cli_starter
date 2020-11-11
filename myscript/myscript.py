import csv
import logging
import sys

import click
import click_log  # type: ignore
import requests

log = logging.getLogger(__name__)
click_log.basic_config(log)

accounts_endpoint = 'http://interview.wpengine.io/v1/accounts'


@click.command()
@click_log.simple_verbosity_option(log)
@click.argument('input_file', type=click.File('r'))
@click.argument('output_file', type=click.File('w'))
def cli(input_file, output_file):
    """
    A tool to merge a CSV file containing customer data with data from the
    `/accounts` endpoint
    """
    try:
        log.debug('Accounts endpoint set to: {}'.format(accounts_endpoint))
        merge_accounts_data(input_file, output_file)
    except Exception as e:
        log.error('An unexpected error occurred.')
        log.exception(e)
        sys.exit(1)


def merge_accounts_data(input_file, output_file):
    """
    Iterator over the items in the CSV file, pull status information from the
    accounts service and write the updated fields to the output file

    :param input_file: open file descriptor to the input csv file
    :param output_file: open file descriptor the output csv file
    """
    accounts = _read_csv(input_file)

    fieldnames = ['Account ID',
                  'Account Name',
                  'First Name',
                  'Created On',
                  'Status',
                  'Status Set On']

    wr = _setup_csv_writer(output_file, fieldnames)
    for account_info in accounts:
        account_id = account_info['Account ID']
        log.debug('Processing account data for {}'.format(account_id))
        account_status_data = _get_account_data(account_id)
        account_info.update(account_status_data)
        del account_info['account_id']
        _write_csv(wr, account_info)


def _setup_csv_writer(output_file, fieldnames):
    try:
        log.debug('Setup Dictwriter to write to {}'.format(output_file))
        wr = csv.DictWriter(output_file, fieldnames=fieldnames)
        wr.writeheader()
        return wr
    except Exception as e:
        log.error('Error occurred while writing contents to {}. {}'.format(
            output_file, e))
        raise


def _write_csv(wr, account_data):
    """
    Write a line of account data to a DictWriter instance with an open file

    :param wr: an open and setup DictWriter
    :param account_data: An ordered dict with the corresponding data to the
        fields contained in the DictWriter
    """
    try:
        log.debug('Writing {} to {}'.format(account_data, wr))
        wr.writerow(account_data)
    except Exception as e:
        log.error('Error occurred while data to the output file: {}.', e)
        raise


def _read_csv(input_file):
    """
    Read in a CSV file and parse the data

    :param input_file: file descriptor to be read from
    :return: Iterator for each data line in the input file
    """
    try:
        log.debug('Reading csv data from {}'.format(input_file))
        csv_iter = csv.DictReader(input_file)
        return csv_iter
    except Exception as e:
        log.error('An error occurred while reading from file {}. {}'
                  .format(input_file, e))
        sys.exit(1)


def _get_account_data(account_id):
    """
    Request account status information from the accounts API and update the
    fields.

    :param account_id: the account id number
    :return:
        A dictionary with the fields ("account_id", "Status", "Status Set On").
        If the response is not available or cannot be found, return
        {"account_id": <account_id>} and the corresponding values will be empty
    """

    account_status = {'account_id': account_id}
    try:
        endpoint_url = accounts_endpoint + '/{id}'
        resp = requests.get(endpoint_url.format(id=account_id),
                            headers={
                                'content-type': 'charset=utf-8'
                            })
        if resp.status_code == 404:
            log.debug('Received 404 from accounts service: {}'.format(resp))
            return account_status
        account_status = resp.json(parse_int=str)
        log.debug('Received {} from accounts endpoint for account {}'
                  .format(resp, account_id))
        account_status['account_id'] = account_id
        account_status['Status'] = account_status.get('status')
        del account_status['status']
        account_status['Status Set On'] = account_status.get('created_on')
        del account_status['created_on']
        return account_status
    except requests.HTTPError as e:
        log.warning('Retrieving account information for account_id: {}. {}'
                    .format(account_id, e))
    return account_status


if __name__ == '__main__':
    cli()
