# emlAnalyzer
A cli script to analyze an E-Mail in the eml format for viewing the header, extracting attachments etc.

## Installation

Install the package with pip

    pip install eml-analyzer

## Usage
Type ```emlAnalyzer --help``` to view the help.

```
usage: emlAnalyzer [OPTION]... [FILE]

A cli script to analyze an E-Mail in the eml format for viewing the header, extracting attachments etc.

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