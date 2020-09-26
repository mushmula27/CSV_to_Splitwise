from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser
from dotenv import load_dotenv
from flask import Flask, redirect, session, request, url_for, jsonify
import os
import csv
import random
import hashlib
import json

load_dotenv()

CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
CONSUMER_KEY = os.getenv("CONSUMER_KEY")

CSV_FILE_LOCATION = os.getenv("CSV_FILE_LOCATION")
print(CSV_FILE_LOCATION)

DB = os.getenv("DB_FILE")
db = {}

# Create splitwise instance
sObj = Splitwise(CONSUMER_KEY,CONSUMER_SECRET)

# Get debug logs
# Splitwise.setDebug(True)

app = Flask(__name__) # make new flask instance
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/;kaseuyfr98348rohlsv'

@app.route('/auth')
def auth():
    url, secret = sObj.getAuthorizeURL()
    session['secret'] = secret
    return redirect(url)

@app.route('/callback')
def callback():
    oauth_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')
    access_token = sObj.getAccessToken(oauth_token,session['secret'],oauth_verifier)
    session['access_token'] = access_token

    return redirect(url_for('main'))

@app.route('/')
def main():
    if 'access_token' in session:
        sObj.setAccessToken(session['access_token'])
        user = sObj.getCurrentUser()
        friends = sObj.getFriends()
        friends_dict = {friend.getFirstName():friend.getId() for friend in friends}
        groups = sObj.getGroups()
        group_list = [group.getName() for group in groups]
        group_id = [group.getId() for group in groups]
        group_dict = {group.getName():group for group in groups}

        with open(CSV_FILE_LOCATION, encoding='utf-8-sig') as data:
            importedData = list(csv.DictReader(data))
            # print(importedData)

            ##### Vet csv before proceeding #####
        for i, row in enumerate(importedData):
            if not (row.get('Debit') and row.get('Payer') and row.get('Group')):
                return f"Remove blanks on row {i+1} in your CSV and try again."

        with open(DB) as db_json:
            db = json.load(db_json)

        msg = []

        # Begin loop reading the CSV
        for row in importedData:
            rowstring = f"{row.get('Date')}, {row.get('Debit')}, {row.get('Description')}, {row.get('Group')}, {row.get('Payer')}"
            rsbytes = bytes(rowstring, 'utf-8')
            hash_obj = hashlib.sha256(rsbytes)
            hex_dig = hash_obj.hexdigest()
            # print(hex_dig)
            if hex_dig in db:
                msg.append(f"{rowstring} looks like a duplicate, skipping")
                continue
            else:
                db[hex_dig] = "True"


            expense = Expense()
            price = float(row['Debit'] or 0)
            expense.setCost(price)
            expense.setDate(row['Date'])
            expense.setDescription(row['Description'])
            expense.setGroupId(group_dict[row['Group']].getId())
            members = group_dict[row['Group']].getMembers()
            users = []

            for member in members:
                user = ExpenseUser()
                user.setId(member.getId())
                if member.getFirstName() == row['Payer']:
                    user.setPaidShare(price)
                else:
                    user.setPaidShare(0)
                users.append(user)

            paid = 0
            share = round(price/len(users),2)
            for user in users:
                user.setOwedShare(share)
                paid = paid + share
            diff = price - paid
            if diff != 0:
                user = random.choice(users)
                user.setOwedShare(share + diff)


            expense.setUsers(users)

            expense = sObj.createExpense(expense)

        msg.append('Import successful!')

        with open(DB, 'w') as outfile:
            json.dump(db, outfile)
            msg.append('New entries recorded in db.')

        message = "<br>".join(msg)
        return message


    return 'User is not logged in'
