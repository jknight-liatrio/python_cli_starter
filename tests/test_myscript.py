from collections import Iterable, OrderedDict
import os
from unittest.mock import MagicMock, patch

from click.testing import CliRunner
from myscript.myscript import (_get_account_data,
                               _read_csv,
                               _setup_csv_writer,
                               _write_csv,
                               accounts_endpoint,
                               cli)
import pytest
import requests


@pytest.fixture()
def input_csv_path():
    """A fixture for the the file path of the sample input.csv"""
    file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             'fixtures', 'input.csv')
    return file_path


@pytest.fixture()
def csv_test_path():
    """A fixture providing test data for operatoring on a csv"""
    file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             'fixtures', 'test.csv')
    return file_path


def test_help():
    """Make sure that help functionality works"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0


@patch('myscript.myscript._get_account_data')
def test_file_interface(mock_account_data, input_csv_path, tmpdir):
    """Mock the return value of account response"""

    mock_account_data.return_value = {
        'account_id': 9999,
        'Status': 'good',
        'Status Set On': '2000-10-20'
    }
    output_file = os.path.join(tmpdir, 'output.csv')
    runner = CliRunner()
    result = runner.invoke(cli, [input_csv_path, output_file])
    assert result.exit_code == 0


@patch('myscript.myscript._get_account_data')
def test_file_interface_empty_data(mock_account_data, input_csv_path, tmpdir):
    """Assert functionality if accounts endpoint throws errors"""

    mock_account_data.return_value = {'account_id': 0000}

    output_file = os.path.join(tmpdir, 'output.csv')
    validation_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   'fixtures', 'output_empty_fields.csv')

    runner = CliRunner()
    result = runner.invoke(cli, [input_csv_path, output_file])
    assert result.exit_code == 0
    with open(output_file) as o:
        with open(validation_file) as v:
            assert o.readlines() == v.readlines()


def test_full_cli_test(input_csv_path, tmpdir):
    """Full execution of the application as expected using input.csv"""

    output_file = os.path.join(tmpdir, 'output.csv')
    runner = CliRunner()
    result = runner.invoke(cli, [input_csv_path, output_file])
    assert result.exit_code == 0


def test_invalid_input_file():
    """Make sure that invalid input file throws error"""

    runner = CliRunner()
    result = runner.invoke(cli, ['howdy', 'output.csv'])
    assert result.exit_code == 2


def test_read_csv(csv_test_path):
    """Assert that returns an iterator"""
    with open(csv_test_path) as f:
        data = _read_csv(f)
        assert isinstance(data, Iterable)


def test_write_csv(tmpdir):
    """
    Validate that providing a list of OrderedDict objects to the write csv
    function produces the expected CSV file
    """
    output_file = os.path.join(tmpdir, 'output.csv')
    test_data = [
        OrderedDict([('a', 1), ('b', 2), ('c', 3)]),
        OrderedDict([('a', 4), ('b', 5), ('c', 6)]),
        OrderedDict([('a', 4), ('b', 5), ('c', 6)])
    ]
    fields = ['a', 'b', 'c']

    with open(output_file, 'w') as f:
        wr = _setup_csv_writer(f, fields)
        for d in test_data:
            _write_csv(wr, d)

    with open(output_file) as o:
        output_data = o.readlines()

    assert output_data[0] == 'a,b,c\n'
    assert output_data[1] == '1,2,3\n'
    assert output_data[2] == '4,5,6\n'
    assert output_data[3] == '4,5,6\n'


def test_write_csv_invalid_csv(tmpdir):
    """
    Validate that providing a list of OrderedDict objects to the write csv
    function produces the expected CSV file
    """
    output_file = os.path.join(tmpdir, 'output.csv')
    test_data = [
        OrderedDict([('a', 1), ('b', 2)]),
        OrderedDict([('a', 4), ('b', 5), ('c', 6)]),
        OrderedDict([('a', 4), ('b', 5), ('c', 6)])
    ]
    fields = ['a', 'b']

    with pytest.raises(Exception):
        with open(output_file, 'w') as f:
            wr = _setup_csv_writer(f, fields)
            for d in test_data:
                _write_csv(wr, d)


def test_write_csv_missing_file_descriptor(tmpdir):
    """
    Assert that an invalid file being passed throws exception
    """
    output_file = os.path.join(tmpdir, 'howdy')
    fields = ['a', 'b', 'c']

    with pytest.raises(TypeError):
        _setup_csv_writer(output_file, fields)

    with pytest.raises(FileNotFoundError):
        with open(output_file) as f:
            _setup_csv_writer(f, fields)

    with pytest.raises(TypeError):
        with open(output_file, 'wb') as f:
            _setup_csv_writer(f, fields)


@pytest.mark.integrationtest
def test_account_endpoint_valid_response():
    """Test the account endpoint and validate it returns expected data"""
    # Get current account data in case the structure changes
    valid_account_id = None
    try:
        resp = requests.get(accounts_endpoint)
        accounts_data = resp.json()
        valid_account_id = accounts_data.get('results')[0].get('account_id')
    except requests.HTTPError:
        pytest.skip('Failed to get data from endpoint. Endpoint is down. ')
    if valid_account_id:
        result = _get_account_data(valid_account_id)
        assert result['account_id'] == valid_account_id


@pytest.mark.integrationtest
def test_account_endpoint_no_account_found():
    """Test the account endpoint with response that is not found"""
    # Get current account data in case the structure changes
    result = _get_account_data('00000')
    assert result.get('account_id') == '00000'


@patch('requests.get')
def test_account_endpoint_mock_no_account_found(mock_requests):
    """Test the account endpoint with response that is not found"""
    mock_object = MagicMock()
    mock_object.status_code = 404
    mock_requests.return_value = mock_object

    result = _get_account_data('00000')
    assert result == {'account_id': '00000'}


@patch('requests.get')
def test_account_data_endpoint_exception(mock_requests):
    """Test account endpoint and throw an http error """

    def my_function(*args, **kwargs):
        raise requests.HTTPError('random error')

    mock_requests.side_effect = my_function
    account_id = '0000'
    result = _get_account_data(account_id)
    assert result == {'account_id': account_id}
