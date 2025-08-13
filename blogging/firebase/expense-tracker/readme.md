## General Steps

1. npm install -g firebase-tools
2. firebase login
    - Select google-personal gmail for learning.
3. firebase init hosting
    - do not overwrite the index.html (since we coded already with our custom logic)
4. firebase deploy

## Steps on Firebase Console 
- Go to Firebase Console
- Create a project named `expenses-tracker`
- Create and select `web app`.
- Under Build -> `Authentication`
  - Sign-in method used is `Email/Password`
  - whenever we do a signup, that user's email is reflected in `Users` tab under Authentication.
- Now, go to `Firestore Database`, 
  - Create a `default` database
  - Created indexes for queries to work. (the index fields and links were auto-suggested in google chrome console logs)
  - Added Rules , firestore_general.rules is the one which can be used by anyone.
    - For more restrictive rules, use firestore_private.rules
  - One can inspect collections in `Data` tab in database.
    - `uid` identifies the user.
    - When user logs in, that corresponding `uid` is derived and used in fetching records. 
- To avoid caching issue which leads to sometimes old pages (despite update to html), i use the below pattern ?v=<version_number>
  - <script defer src="app.js?v=3"></script>
  - In case, i release any new change, i just bump the version to say 4 and the changes are reflected.


## Testing
- For quick testing, try `testMode=true` in app.js. This avoids all calls and we can quickly test the UI.
- As such, we can use `VS Live Preview Extension` to view the changes locally.
- Once we are satisified
  

## Suggested Prompt in GPT

I want to write a expense tracker app in firebase. it should use free-tier. It should have authentication and allow user store the transaction information : date, amount , category. 

Provided detailed step by step procedure to achieve this. 

I would like to store it in Firebase DB. 

For Authentication, I prefer to use username+password ( email + password). 

---

## 🔧 Tools and Stack

* **Frontend**: HTML/CSS + JavaScript (or React/Flutter depending on your choice)
* **Backend (optional)**: Cloud Functions (optional, can be added later)
* **Firebase Services Used**:

  * Firebase Authentication
  * Firebase Firestore (or Realtime Database)
  * Firebase Hosting (optional for deployment)
* **Free-tier Limitations** (as of 2025):

  * Firestore: 50K reads/day, 20K writes/day
  * Auth: 10K verifications/month
  * Hosting: 1 GB storage / 10 GB transfer

---

## ✅ Step-by-Step Guide

---

### 1. **Create Firebase Project**

* Go to [https://console.firebase.google.com](https://console.firebase.google.com)
* Click **“Add project”**
* Name your project (e.g., `ExpenseTrackerApp`)
* Disable Google Analytics (optional)
* Finish setup

---

### 2. **Enable Firebase Authentication (Email + Password)**

* In your Firebase Console:

  * Go to **Build → Authentication**
  * Click **“Get started”**
  * Go to **Sign-in method** tab
  * Enable **Email/Password** provider

---

### 3. **Create Firestore Database**

You can choose **Firestore** (preferred) or **Realtime Database**.

#### To use Firestore:

* Go to **Build → Firestore Database**
* Click **Create database**
* Choose **Start in test mode** (for development; restrict later)
* Select the Cloud Firestore location

---