# CSV to Splitwise

A simple script to create Splitwise expenses from a CSV file using the [Splitwise API](https://github.com/namaggarwal/splitwise) for Python running a Flask application.

Currently the script assumes expenses are split equally.
An expense group should be created in Splitwise beforehand and any group members need to be added to it.

Your CSV file must have headers:

- `Date`: Date of transaction
- `Description`: Transaction description
- `Debit`: Transaction amount _formatted as a number_
- `Payer`: The payer's **first name**
- `Group`: Group name where the transaction should go

## Getting started

Register your application on [Splitwise](https://secure.splitwise.com/oauth_clients) to obtain a consumer key and consumer secret.

In `.env_example` fill in your consumer key, consumer secret and your CSV file location.
Change `.env_example` to `.env`.

Instal all requirements from terminal

```
$ pip install -r requirements.txt
```

Run `./startserver.sh` in terminal.

Go to http://localhost:5000/ and authorise the application in Splitwise as prompted.

## Future goals

- Deploy the application and build a simple UI
- Allow payer to be identified by more than first name, eg. full name, surname, email
- Allow custom shares
- Allow group creation from directly from CSV
- Clean up code as not all information is used at the moment
