# emlAnalyzer
A CLI script to analyze an email in the EML format for viewing headers, extracting attachments, etc.

## Installation

Install the package with pip

    pip install eml-analyzer

## Usage
Type ```emlAnalyzer --help``` to view the help.

```
usage: emlAnalyzer [-h] [-i [INPUT]] [--header] [-x] [-a] [--text] [--html] [-s] [-u] [-ea EXTRACT] [--extract-all] [-o OUTPUT] [--format [{json}]]

A CLI script to analyze an email in the EML format for viewing headers, extracting attachments, etc.

optional arguments:
  -h, --help            show this help message and exit
  -i [INPUT], --input [INPUT]
                        Path to the EML file. Accepts standard input if omitted
  --header              Shows the headers
  -x, --tracking        Shows content which is reloaded from external resources in the HTML part
  -a, --attachments     Lists attachments
  --text                Shows plaintext
  --html                Shows HTML
  -s, --structure       Shows structure of the E-Mail
  -u, --url             Shows embedded links and urls in the HTML and text part
  -ea EXTRACT, --extract EXTRACT
                        Extracts the x-th attachment. Can not be used together with the '--format' parameter.
  --extract-all         Extracts all attachments. If a output format is specified the content of the attachments will be included in the structural output as a base64 encoded blob
  -o OUTPUT, --output OUTPUT
                        Path for the extracted attachment (default is filename in working directory)
  --format [{json}]     Specifies a structured output format, the default format is not machine-readable
```

## Examples

### Example 1
```
$ emlAnalyzer -i email_1.eml
 =================
 ||  Structure  ||
 =================
|- text/html

 =========================
 ||  URLs in HTML part  ||
 =========================
 - https://suspicious.site.com/Zajnad

 ===============================================
 ||  Reloaded Content (aka. Tracking Pixels)  ||
 ===============================================
[+] No content found which will be reloaded from external resources

 ===================
 ||  Attachments  ||
 ===================
[+] E-Mail contains no attachments

```

### Example 2
```
$ emlAnalyzer -i email_2.eml
 =================
 ||  Structure  ||
 =================
|- multipart/mixed
|  |- multipart/related
|  |  |- text/html
|  |  |- image/jpeg                        [image002.jpg]
|  |  |- image/jpeg                        [image003.jpg]
|  |  |- image/png                         [image004.png]
|  |- message/rfc822
|  |  |- multipart/alternative
|  |  |  |- text/plain
|  |  |  |- text/html

 =========================
 ||  URLs in HTML part  ||
 =========================
 - https://example.company.com/random/link
 - mailto:john.doe@company.com

 ===============================================
 ||  Reloaded Content (aka. Tracking Pixels)  ||
 ===============================================
[+] No content found which will be reloaded from external resources

 ===================
 ||  Attachments  ||
 ===================
[1] image002.jpg        image/jpeg        inline
[2] image003.jpg        image/jpeg        inline
[3] image004.png        image/png         inline

```

### Example 3
```
$ emlAnalyzer -i email_1.eml --header

 ==============
 ||  Header  ||
 ==============
From..........................................John Doe <asjkasd@asdasd123.com>
To............................................"bob@company.at" <bob@company.at>
Subject.......................................RANDOM SUBJECT
Thread-Topic..................................RANDOM SUBJECT
X-MS-Exchange-MessageSentRepresentingType.....1
Date..........................................Tue, 19 May 2020 07:02:37 +0000
Accept-Language...............................de-DE, en-US
Content-Language..............................de-DE
X-MS-Exchange-Organization-AuthAs.............Anonymous
X-MS-Has-Attach...............................
X-MS-TNEF-Correlator..........................
x-fireeye.....................................Clean
x-rmx-source..................................123.123.123.123
Content-Type..................................text/html; charset="iso-8859-1"
Content-Transfer-Encoding.....................quoted-printable
MIME-Version..................................1.0
```

### Example 4
```json
$ emlAnalyzer -i email_4.eml --format json
{
    "structure": {
        "type": "multipart/mixed",
        "children": [
            {
                "type": "text/plain"
            },
            {
                "type": "application/pdf",
                "name": "attachment_123.pdf",
                "disposition": "attachment"
            }
        ]
    },
    "urls": [
        "https://www.facebook.de/abc123",
        "https://www.google.com/demo"
    ],
    "reloaded_content": [],
    "attachments": [
        {
            "type": "application/pdf",
            "name": "attachment_123.pdf",
            "disposition": "attachment"
        }
    ]
}
```