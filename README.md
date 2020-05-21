# emlAnalyzer
A cli script to analyze an E-Mail in the eml format for viewing the header, extracting attachments etc.

## Installation

Install the package with pip

    pip install eml-analyzer

## Usage
Type ```emlAnalyzer --help``` to view the help.

```
usage: emlAnalyzer [OPTION]... [FILE]

Lists information about the FILEs (the current directory by default) including Alternate Data Streams.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to the eml-file (is required)
  --header              Shows the headers
  -x, --tracking        Shows content which is reloaded from external ressources in the HTML part
  -a, --attachments     Lists attachments
  --text                Shows plaintext
  --html                Shows HTML
  -s, --structure       Shows structure of the E-Mail
  -u, --url             Shows embedded links and urls in the html part
  -ea EXTRACT, --extract EXTRACT
                        Extracts the x-th attachment
  -o OUTPUT, --output OUTPUT
                        Path for the extracted attachment (default is filename in working directory)
```

## Examples

### Example 1
```
$ COMMAND
TODO
```

### Example 2
```
$ COMMAND
TODO
```
