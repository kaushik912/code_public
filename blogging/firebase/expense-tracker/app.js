// Firebase config
const firebaseConfig = {
  apiKey: "<your_key>",
  authDomain: "expenses-tracker-3352f.firebaseapp.com",
  projectId: "<project_id>",
  storageBucket: "expenses-tracker-3352f.firebasestorage.app",
  messagingSenderId: "924419386388",
  appId: "1:924419386388:web:dd7901678415da486fcb01",
  measurementId: "G-K83YZ0TS8R",
};

// Toggle this to use mock data instead of Firebase
const testMode = false;

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();

if (testMode) {
  document.getElementById("loginSection").style.display = "none";
  document.getElementById("appSection").style.display = "block";
  loadMockExpenses();
} else {
  auth.onAuthStateChanged((user) => {
    if (user) {
      document.getElementById("loginSection").style.display = "none";
      document.getElementById("appSection").style.display = "block";
      initializeMonthFilter(); // Initialize with current month
    } else {
      document.getElementById("loginSection").style.display = "block";
      document.getElementById("appSection").style.display = "none";
    }
  });
}

function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  auth.signInWithEmailAndPassword(email, password).catch((err) => {
    document.getElementById("authMsg").textContent = err.message;
  });
}

function signup() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  auth.createUserWithEmailAndPassword(email, password).catch((err) => {
    document.getElementById("authMsg").textContent = err.message;
  });
}

function logout() {
  auth.signOut();
}

document.getElementById("expenseForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const amount = document.getElementById("amount").value;
  const date = document.getElementById("date").value;
  const category = document.getElementById("category").value;

  if (testMode) {
    alert("Adding expenses is disabled in test mode.");
    return;
  }

  const user = auth.currentUser;
  if (!user) return;

  await db.collection("expenses").add({
    uid: user.uid,
    amount,
    date,
    category,
  });

  // Apply current filter
  filterByMonth();
  e.target.reset();
});

async function loadExpenses(filterMonth = null) {
  const user = auth.currentUser;
  if (!user) return;

  let query = db.collection("expenses").where("uid", "==", user.uid);

  // Apply month filter if provided
  if (filterMonth) {
    const [year, month] = filterMonth.split("-");
    const startDate = `${year}-${month}-01`;

    // Calculate the end date (first day of next month)
    let endMonth = parseInt(month);
    let endYear = parseInt(year);
    if (endMonth === 12) {
      endMonth = 1;
      endYear += 1;
    } else {
      endMonth += 1;
    }
    const endDate = `${endYear}-${endMonth.toString().padStart(2, "0")}-01`;

    query = query.where("date", ">=", startDate).where("date", "<", endDate);
  }

  const snapshot = await query.orderBy("date", "desc").get();
  const expenses = snapshot.docs.map((doc) => ({
    id: doc.id,
    ...doc.data(),
  }));
  renderExpenses(expenses);
}

async function loadMockExpenses() {
  const response = await fetch("mock_expenses.json");
  const mockData = await response.json();
  // Add mock IDs to the expenses
  const expensesWithIds = mockData.map((expense, index) => ({
    id: `mock-id-${index}`,
    ...expense,
  }));
  renderExpenses(expensesWithIds);
}

function renderExpenses(data) {
  const list = document.getElementById("expenseList");
  const selectedMonthTotalEl = document.getElementById("selectedMonthTotal");

  list.innerHTML = "";

  let selectedMonthTotal = 0;

  data.forEach(({ id, amount, date, category }) => {
    const amountNum = parseFloat(amount);
    selectedMonthTotal += amountNum;

    list.innerHTML += `
      <tr data-id="${id}">
        <td>${date}</td>
        <td>${amountNum.toFixed(2)}</td>
        <td>${category}</td>
        <td>
          <button onclick="openEditModal('${id}', '${amount}', '${date}', '${category}')" class="edit-btn">Edit</button>
          <button onclick="deleteExpense('${id}')" class="delete-btn">Delete</button>
        </td>
      </tr>`;
  });

  selectedMonthTotalEl.textContent = selectedMonthTotal.toFixed(2);
}

// Filter expenses by month
function filterByMonth() {
  const monthValue = document.getElementById("monthFilter").value;
  if (monthValue) {
    loadExpenses(monthValue);
  } else {
    loadExpenses();
  }
}

// Reset filter to show all expenses
function resetFilter() {
  document.getElementById("monthFilter").value = "";
  loadExpenses();
}

// Initialize month filter with current month
function initializeMonthFilter() {
  const now = new Date();
  const year = now.getFullYear();
  const month = (now.getMonth() + 1).toString().padStart(2, "0");
  document.getElementById("monthFilter").value = `${year}-${month}`;
  filterByMonth();
}

// Open edit modal with expense details
function openEditModal(id, amount, date, category) {
  document.getElementById("editId").value = id;
  document.getElementById("editAmount").value = amount;
  document.getElementById("editDate").value = date;
  document.getElementById("editCategory").value = category;
  document.getElementById("editModal").style.display = "block";
}

// Close edit modal
function closeEditModal() {
  document.getElementById("editModal").style.display = "none";
}

// Delete expense
async function deleteExpense(id) {
  if (testMode) {
    alert("Deleting expenses is disabled in test mode.");
    return;
  }

  if (confirm("Are you sure you want to delete this expense?")) {
    const user = auth.currentUser;
    if (!user) return;

    await db.collection("expenses").doc(id).delete();

    // Refresh the expense list
    filterByMonth();
  }
}

// Initialize edit form submission handler
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("editForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    if (testMode) {
      alert("Editing expenses is disabled in test mode.");
      closeEditModal();
      return;
    }

    const id = document.getElementById("editId").value;
    const amount = document.getElementById("editAmount").value;
    const date = document.getElementById("editDate").value;
    const category = document.getElementById("editCategory").value;

    const user = auth.currentUser;
    if (!user) return;

    await db.collection("expenses").doc(id).update({
      amount,
      date,
      category,
    });

    closeEditModal();

    // Refresh the expense list
    filterByMonth();
  });
});

// Export data as JSON
async function exportData() {
  if (testMode) {
    alert("Export is disabled in test mode.");
    return;
  }

  const user = auth.currentUser;
  if (!user) return;

  try {
    // Get all expenses for the current user
    const snapshot = await db.collection("expenses").where("uid", "==", user.uid).get();
    const expenses = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));

    // Create a download link with the JSON data
    const dataStr = JSON.stringify(expenses, null, 2);
    const dataUri = "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);
    
    const exportFileName = `expense_tracker_backup_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileName);
    linkElement.click();
  } catch (error) {
    alert(`Error exporting data: ${error.message}`);
  }
}

// Open import modal
function openImportModal() {
  if (testMode) {
    alert("Import is disabled in test mode.");
    return;
  }
  
  document.getElementById("importModal").style.display = "block";
}

// Close import modal
function closeImportModal() {
  document.getElementById("importModal").style.display = "none";
  document.getElementById("importData").value = "";
}

// Import data from JSON
async function importData() {
  if (testMode) {
    alert("Import is disabled in test mode.");
    closeImportModal();
    return;
  }

  const user = auth.currentUser;
  if (!user) return;

  try {
    const jsonData = document.getElementById("importData").value;
    if (!jsonData) {
      alert("Please paste valid JSON data.");
      return;
    }

    const expenses = JSON.parse(jsonData);
    
    if (!Array.isArray(expenses)) {
      alert("Invalid data format. Expected an array of expenses.");
      return;
    }
    
    const batch = db.batch();
    let count = 0;
    
    // Process each expense
    for (const expense of expenses) {
      // Make sure expense has the required fields
      if (!expense.amount || !expense.date || !expense.category) {
        continue;
      }
      
      // Create a new document reference if we don't have the ID
      // or use the existing ID if available
      const expenseRef = expense.id ? 
        db.collection("expenses").doc(expense.id) : 
        db.collection("expenses").doc();
      
      // Set the document data (ensure current user is the owner)
      batch.set(expenseRef, {
        uid: user.uid,
        amount: expense.amount,
        date: expense.date,
        category: expense.category
      });
      
      count++;
    }
    
    // Commit the batch write
    await batch.commit();
    
    alert(`Successfully imported ${count} expenses.`);
    closeImportModal();
    
    // Refresh the expense list
    filterByMonth();
  } catch (error) {
    alert(`Error importing data: ${error.message}`);
  }
}

// Password Update Functions
function openPasswordModal() {
  if (testMode) {
    alert("Password update is disabled in test mode.");
    return;
  }
  
  // Clear previous messages and fields
  document.getElementById("passwordMsg").textContent = "";
  document.getElementById("currentPassword").value = "";
  document.getElementById("newPassword").value = "";
  document.getElementById("confirmPassword").value = "";
  
  document.getElementById("passwordModal").style.display = "block";
}

function closePasswordModal() {
  document.getElementById("passwordModal").style.display = "none";
}

async function updatePassword() {
  if (testMode) {
    alert("Password update is disabled in test mode.");
    closePasswordModal();
    return;
  }
  
  const currentPassword = document.getElementById("currentPassword").value;
  const newPassword = document.getElementById("newPassword").value;
  const confirmPassword = document.getElementById("confirmPassword").value;
  const msgElement = document.getElementById("passwordMsg");
  
  // Validate inputs
  if (!currentPassword || !newPassword || !confirmPassword) {
    msgElement.textContent = "All fields are required.";
    return;
  }
  
  if (newPassword !== confirmPassword) {
    msgElement.textContent = "New passwords do not match.";
    return;
  }
  
  if (newPassword.length < 6) {
    msgElement.textContent = "New password must be at least 6 characters.";
    return;
  }
  
  try {
    const user = auth.currentUser;
    if (!user) return;
    
    // Get the user's email
    const email = user.email;
    
    // Reauthenticate the user first
    const credential = firebase.auth.EmailAuthProvider.credential(email, currentPassword);
    await user.reauthenticateWithCredential(credential);
    
    // Update the password
    await user.updatePassword(newPassword);
    
    alert("Password updated successfully!");
    closePasswordModal();
  } catch (error) {
    // Handle specific error codes
    if (error.code === 'auth/wrong-password') {
      msgElement.textContent = "Current password is incorrect.";
    } else {
      msgElement.textContent = error.message;
    }
  }
}
