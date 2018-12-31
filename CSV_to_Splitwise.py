from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser
from dotenv import load_dotenv
from flask import Flask, redirect, session, request, url_for, jsonify
import os
import csv
import random

load_dotenv()

CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
CONSUMER_KEY = os.getenv("CONSUMER_KEY")

CSV_FILE_LOCATION = os.getenv("CSV_FILE_LOCATION")

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
        print(group_list, group_id, group_dict, friends_dict)

        with open(CSV_FILE_LOCATION) as data:
            importedData = list(csv.DictReader(data))


# Begin loop reading the CSV
        for row in importedData:
            expense = Expense()
            price = float(row['Debit'])
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
        return 'Import successful!'


    return 'User is not logged in'
