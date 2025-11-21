# PyWhooshConnect

**Whoosh your Garmin workouts!**

Convert your Garmin training plans to MyWhoosh workouts in seconds. Download, convert, upload and
ride.

## About

PyWhooshConnect is a command-line tool that synchronizes your Garmin Connect workouts and converts
them into MyWhoosh-compatible format. It automatically fetches your scheduled workouts from Garmin
Connect, converts them to `.json` files, and prepares them for upload to MyWhoosh.

The tool supports multiple sports (cycling, running, cross-country skiing) and allows flexible
configuration of power zones and workout parameters through YAML configuration files.

## Installation

**Requirements:** Python 3.13+ (tested with Python 3.13)

```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt # optional, required only for development
```

**Note:** This tool uses [garminconnect](https://github.com/cyberjunky/python-garminconnect) library
to interact with Garmin Connect API.

## Usage

Run the application from the command line:

```bash
python main.py [OPTIONS]
```

For a complete list of available options and their descriptions, run `python main.py --help`.

### Basic Example

```bash
python main.py --user your.email@example.com --sport cycling --from-date 2025-01-01 --to-date 2025-01-07
```

### Authentication

You can provide your Garmin Connect credentials in three ways (in order of priority):

1. **Command-line arguments**: `--user` and `--password`

2. **Environment variables**:
   Create a `.env` file in the project root (see [`.env.example`](.env.example) for reference):

3. **Interactive prompt**:
   If credentials are not provided through the above methods, the application will prompt you to
   enter them at startup.

### Configuration File

You can customize power zones and workout parameters using a YAML configuration file with the
`--config-file` option.

If no configuration file is specified, the tool uses the default configuration from [
`config/power_zones_config.yml`](pywhooshconnect/config/power_zones_config.yml).

### Output

Workouts are saved as `.json` files in the directory specified by `--output-dir` (default:
`~/downloads/`).

### Uploading to MyWhoosh

After downloading your workouts:

1. Go to [MyWhoosh Workout Builder](https://workout.mywhoosh.com/) and login in your MyWhoosh
   account
2. Select **Create New Workout**
3. Click **Import workout**
4. Upload the `.json` file from your output directory
5. Click **Export to MyWhoosh**

Your workout will be available in the **Custom Workouts** section of your MyWhoosh profile.

## Contributing

If you wish to contribute or you have just found any bug, please open an issue or a pull request on
our GitHub repository. Thank you!

## License

PyWhooshConnect is licensed under
the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) - see
the [LICENSE](LICENSE) file for details.
