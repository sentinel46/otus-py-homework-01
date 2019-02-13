# otus-py homework 01

nginx log files analyzer
calculates `REPORT_SIZE` longest url requests from latest nginx log file

## Usage

```
log_analyzer.py [--config=config_file]
```

## Configuration

configuration stored in JSON format
available options:
- REPORT_SIZE -- number of urls stored in report
- REPORT_DIR  -- directory where log_analyzer stores reports
- LOG_DIR     -- directory with logs to analyze. log_analyzer works with latest log file
- ERROR_RATE  -- the ratio of total requests number in error to the total requests number to abort analyzing
- LOG_NAME    -- file to store log_analyzer's working log

## Running the tests

```
cd log_analyzer
python3 -m unittest -v tests.test_log_analyzer
```
