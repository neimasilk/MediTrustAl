# Manual Test Instructions for Frontend Patient Portal

This document contains steps for manually testing frontend functionality, with an initial focus on the Login Page (Mockup-01) and Registration Page (Mockup-02).

**Important Note:** All automated backend tests have passed successfully. The current focus of manual testing is on verifying the frontend implementation.

## Prerequisites (Initial Preparation):

1.  **Backend Server Running:**
    *   Ensure the FastAPI backend server is running. Usually started with a command like `python -m src.app.main` (if in root) or `python -m app.main` from within the `src/` directory.
    *   Verify the backend is accessible, for example, at `http://localhost:8000/docs`.

2.  **Frontend Development Server Running:**
    *   Ensure the Vite frontend development server is running.
    *   Navigate to the `frontend` directory (`cd frontend`).
    *   Run with the command `npm run dev`.
    *   The frontend will be available at `http://localhost:5173` (or another port if 5173 is already in use).

3.  **User Data:**
    *   Prepare at least two patient accounts (Patient A, Patient B) and two doctor accounts (Doctor X, Doctor Y) already registered in the system. Ensure Doctor X and Doctor Y have valid blockchain addresses configured in the database.
    *   You can register new users via the backend API endpoint (`POST /api/v1/auth/register`) using tools like Postman or curl.
    *   Note down the username and password for all these users for login.

4.  **Medical Record Data (Optional):**
    *   To test the display of the medical records list on the dashboard, the logged-in user should ideally have some medical record data.
    *   If not, the dashboard is expected to display a message like "You do not have any medical records yet" or similar. You can create medical records via the backend API endpoint (`POST /api/v1/medical-records`) on behalf of the user who will log in. Ensure these medical records have a `data_hash`.

5.  **Database Access:**
    *   Prepare access to the backend database to verify entries in the `audit_data_access_logs` table.

## Frontend Test Cases:

## A. Frontend Test Cases: Login Page (Mockup-01)

### A.1. Login Page UI Display

*   **Actions:**
    1.  Open a browser (e.g., Chrome, Firefox).
    2.  Navigate to the frontend address, e.g., `http://localhost:5173`.
*   **Expected Results:**
    *   You will be automatically redirected to the `/login` page.
    *   The login page should display:
        *   A title (e.g., "Login" or "Sign In").
        *   An input field for "Username or Email".
        *   An input field for "Password".
        *   A "Login" (or "Sign In") button.

### A.2. Login with Invalid Credentials

*   **Actions:**
    1.  On the login page, enter an incorrect or unregistered username/email and password combination.
    2.  Click the "Login" button.
*   **Expected Results:**
    *   An error message will be displayed on the login page (e.g., "Login Failed. Please check your username/email and password," or the error message from the backend).
    *   You remain on the `/login` page.
    *   Check the browser console (Developer Tools > Console): there should be no fatal errors stopping the application. API response errors (e.g., 401 or 400) are acceptable.

### A.3. Login with Valid Credentials

*   **Actions:**
    1.  On the login page, enter the correct username/email and password for Patient A.
    2.  Click the "Login" button.
*   **Expected Results:**
    *   You will be redirected to the `/dashboard` page.
    *   Open Developer Tools > Application > Local Storage: an item `access_token` (or a similar name defined in `tokenManager.js`) should exist and contain a JWT token.

### A.4. Dashboard Page Display (After Login)

*   **Actions:**
    1.  After successfully logging in as Patient A, you are on the `/dashboard` page.
*   **Expected Results:**
    *   A welcome message is displayed (e.g., "Welcome to Your Dashboard, [Patient A's username]").
    *   A "Logout" (or "Sign Out") button is visible.
    *   **If Patient A has medical records:**
        *   A table or list of medical records will be displayed.
        *   Minimum columns: Record ID, Record Type, Date Created (formatted), Data Hash, and a "Manage Access" button/icon.
        *   The data displayed must correspond to Patient A's medical records.
    *   **If Patient A has no medical records:**
        *   A message like "You do not have any medical records yet" or "No medical record data" will be displayed.

### A.5. Accessing Protected Route (Dashboard)

*   **Actions (When Not Logged In):**
    1.  Ensure you are logged out or open a new incognito window.
    2.  Try accessing `http://localhost:5173/dashboard` directly.
*   **Expected Results (When Not Logged In):**
    *   You will be automatically redirected back to the `/login` page.

*   **Actions (When Logged In):**
    1.  Log in to the application as Patient A, so you are on the `/dashboard` page.
    2.  Refresh the `/dashboard` page (press F5 or the browser's refresh button).
*   **Expected Results (When Logged In):**
    *   You remain on the `/dashboard` page.
    *   Data on the dashboard (including the list of medical records) will reload correctly.

### A.6. Logout Functionality

## B. Frontend Test Cases: Registration Page (Mockup-02)

### B.1. Registration Page UI Display

*   **Actions:**
    1.  Open a browser (e.g., Chrome, Firefox).
    2.  Navigate to the frontend address, then click the "Register here" link from the login page, or go directly to `http://localhost:5173/register`.
*   **Expected Results:**
    *   You will be on the `/register` page.
    *   The registration page should display:
        *   A title (e.g., "Create New Account" or "Register").
        *   An input field for "Email".
        *   An input field for "Username".
        *   An input field for "Full Name".
        *   An input field for "Password".
        *   An input field for "Confirm Password".
        *   (Optional, if in UI) An input field or selection for "Role" (e.g., defaults to 'patient').
        *   (Optional, if in UI) An input field for "Blockchain Address".
        *   A "Register" button.
        *   A link to the login page (e.g., "Already have an account? Login here").

### B.2. Registration with Invalid or Incomplete Data

*   **Actions (Passwords Do Not Match):**
    1.  On the registration page, fill all fields with valid data, but enter different passwords in the "Password" and "Confirm Password" fields.
    2.  Click the "Register" button.
*   **Expected Results (Passwords Do Not Match):**
    *   A frontend validation error message is displayed (e.g., "Password and Confirm Password do not match.").
    *   You remain on the `/register` page.
    *   No request is sent to the backend.

*   **Actions (Invalid Email):**
    1.  On the registration page, enter an invalid email format (e.g., "test@test").
    2.  Fill other fields correctly.
    3.  Click the "Register" button.
*   **Expected Results (Invalid Email):**
    *   A frontend validation error message is displayed (e.g., "Invalid email format.").
    *   You remain on the `/register` page.

*   **Actions (Required Field Empty):**
    1.  Leave a required field empty (e.g., Username).
    2.  Fill other fields correctly.
    3.  Click the "Register" button.
*   **Expected Results (Required Field Empty):**
    *   A frontend validation error message is displayed (e.g., "Username cannot be empty.").
    *   You remain on the `/register` page.

### B.3. Registration with Existing Username or Email

*   **Preparation:**
    *   Ensure a user is already registered with the username `existinguser` and email `existing@example.com`.
*   **Actions (Username Already Exists):**
    1.  On the registration page, enter `existinguser` in the Username field.
    2.  Fill other fields with new, valid data.
    3.  Click the "Register" button.
*   **Expected Results (Username Already Exists):**
    *   An error message from the backend is displayed in the UI (e.g., "Username already taken." or "User with this username already exists").
    *   You remain on the `/register` page.

*   **Actions (Email Already Exists):**
    1.  On the registration page, enter `existing@example.com` in the Email field.
    2.  Fill other fields with new, valid data.
    3.  Click the "Register" button.
*   **Expected Results (Email Already Exists):**
    *   An error message from the backend is displayed in the UI (e.g., "Email already registered." or "User with this email already exists").
    *   You remain on the `/register` page.

### B.4. Successful Registration

*   **Actions:**
    1.  On the registration page, fill all fields with valid and unique (unregistered) data.
    2.  Ensure password and confirm password match.
    3.  Click the "Register" button.
*   **Expected Results:**
    *   A success message is displayed in the UI (e.g., "Registration successful! Please login.").
    *   You are redirected to the `/login` page.
    *   Verify in the backend database: the new user has been created in the `users` table with the corresponding data.
    *   (Optional, if applicable) Verify on the blockchain (Ganache): if registration also registers the user in `UserRegistry`, ensure a new entry exists.

### B.5. Link to Login Page

*   **Actions:**
    1.  On the registration page, click the "Already have an account? Login here" link (or similar text).
*   **Expected Results:**
    *   You are redirected to the `/login` page.

## C. Advanced Frontend Test Cases (After Login & Registration are Stable)
(This section will be filled in later after M01 and M02 are completed and stable)


*   **Actions:**
    1.  Ensure you are logged in and on the `/dashboard` page.
    2.  Click the "Logout" button.
*   **Expected Results:**
    *   You will be redirected back to the `/login` page.
    *   Open Developer Tools > Application > Local Storage: the `access_token` item should be removed.
    *   Attempting to access `http://localhost:5173/dashboard` directly after logout will redirect you back to `/login`.

### 7. UI Consent Management - Grant Access (Test Case 5.1.3)

*   **Preparation:**
    *   Ensure Patient A has at least one medical record.
    *   Ensure Doctor Y has an account and a valid blockchain address.
*   **Actions:**
    1.  Log in as Patient A on the frontend.
    2.  Navigate to the Dashboard.
    3.  For one of Patient A's medical records, click the "Manage Access" button (or similar icon) to open the "Manage Access for Record: [Record ID]" modal.
    4.  In the modal, enter Doctor Y's valid blockchain address in the "Doctor's Blockchain Address" field.
    5.  Click the "Grant Access" button.
*   **Expected Results:**
    *   The UI displays a loading indicator on the "Grant Access" button.
    *   After a moment, the UI displays a success message (e.g., "Access successfully granted to [Doctor Y's Address]").
    *   The doctor's address input field might be cleared or remain filled with Doctor Y's address.
    *   **Backend Verification:** Check the `audit_data_access_logs` table. There should be a new entry with `actor_user_id` = Patient A's ID, `owner_user_id` = Patient A's ID, `action_type` = `'GRANT_ACCESS_SUCCESS'`, `target_address` = Doctor Y's address, and the IP address.
*   **Actions (Invalid Input):**
    1.  In the same modal, clear the "Doctor's Blockchain Address" field.
    2.  Click the "Grant Access" button.
*   **Expected Results (Invalid Input):**
    *   The UI displays a validation error message (e.g., "Doctor's address cannot be empty.").
*   **Actions (Invalid Address Format Input):**
    1.  In the same modal, enter an invalid blockchain address format (e.g., "0x123").
    2.  Click the "Grant Access" button.
*   **Expected Results (Invalid Address Format Input):**
    *   If frontend validation exists, display an error. If not, the backend will return a 422 or 400 error. The API error message (e.g., "Invalid Ethereum address format") should be displayed in the UI.

### 8. UI Consent Management - Revoke Access (Test Case 5.1.4)

*   **Preparation:**
    *   Ensure Doctor Y already has access to one of Patient A's medical records (e.g., from Test Case 5.1.3 results).
*   **Actions:**
    1.  Log in as Patient A on the frontend.
    2.  Navigate to the Dashboard.
    3.  Open the "Manage Access" modal for the medical record to which Doctor Y has access.
    4.  Enter Doctor Y's blockchain address in the "Doctor's Blockchain Address" field.
    5.  Click the "Revoke Access" button.
*   **Expected Results:**
    *   The UI displays a loading indicator on the "Revoke Access" button.
    *   After a moment, the UI displays a success message (e.g., "Access successfully revoked from [Doctor Y's Address]").
    *   **Backend Verification:** Check the `audit_data_access_logs` table. There should be a new entry with `actor_user_id` = Patient A's ID, `owner_user_id` = Patient A's ID, `action_type` = `'REVOKE_ACCESS_SUCCESS'`, `target_address` = Doctor Y's address, and the IP address.
*   **Actions (Invalid Input):**
    1.  In the same modal, clear the "Doctor's Blockchain Address" field.
    2.  Click the "Revoke Access" button.
*   **Expected Results (Invalid Input):**
    *   The UI displays a validation error message (e.g., "Doctor's address to revoke cannot be empty.").

## Backend & API Test Cases (Using Tools like Postman/curl):

### 1. Audit Log Verification for `get_medical_record_detail` (Test Case 4.2.3)

*   **Preparation:**
    *   Patient A has a medical record (RM_A1).
    *   Doctor X has access to RM_A1 (granted previously or as part of test prep).
    *   Doctor Y does not have access to RM_A1.
*   **Action 1: Patient A accesses their own medical record**
    1.  Log in as Patient A (get token).
    2.  Call API `GET /api/v1/medical-records/{RM_A1_ID}` with Patient A's token.
*   **Expected Result 1:**
    *   Successful response (200 OK) with RM_A1 details.
    *   Check `audit_data_access_logs` table in the database: New entry with `actor_user_id` = Patient A's ID, `owner_user_id` = Patient A's ID, `record_id` = RM_A1_ID, `action_type` = `'VIEW_RECORD_SUCCESS'`, and caller's IP address.
*   **Action 2: Doctor X (authorized) accesses Patient A's medical record**
    1.  Log in as Doctor X (get token).
    2.  Call API `GET /api/v1/medical-records/{RM_A1_ID}` with Doctor X's token.
*   **Expected Result 2:**
    *   Successful response (200 OK) with RM_A1 details.
    *   Check `audit_data_access_logs` table: New entry with `actor_user_id` = Doctor X's ID, `owner_user_id` = Patient A's ID, `record_id` = RM_A1_ID, `action_type` = `'VIEW_RECORD_SUCCESS'`, and caller's IP address.
*   **Action 3: Doctor Y (unauthorized) tries to access Patient A's medical record**
    1.  Log in as Doctor Y (get token).
    2.  Call API `GET /api/v1/medical-records/{RM_A1_ID}` with Doctor Y's token.
*   **Expected Result 3:**
    *   Failed response (403 Forbidden or other appropriate error if blockchain access fails).
    *   Check `audit_data_access_logs` table: New entry with `actor_user_id` = Doctor Y's ID, `owner_user_id` = Patient A's ID, `record_id` = RM_A1_ID, `action_type` according to failure scenario (e.g., `'VIEW_RECORD_FAILURE_FORBIDDEN'`, `'VIEW_RECORD_FAILURE_BC_CHECK_FAILED'`), and caller's IP address.

### 2. Audit Log Verification for `grant_medical_record_access` (Test Case 4.2.4)

*   **Preparation:**
    *   Patient A has a medical record (RM_A2) not yet accessed by Doctor X.
    *   Patient B has a medical record (RM_B1).
*   **Action 1: Patient A grants access to RM_A2 to Doctor X**
    1.  Log in as Patient A (get token).
    2.  Call API `POST /api/v1/medical-records/{RM_A2_ID}/grant-access` with Patient A's token and payload `{"doctor_address": "DOCTOR_X_BLOCKCHAIN_ADDRESS"}`.
*   **Expected Result 1:**
    *   Successful response (200 OK).
    *   Check `audit_data_access_logs` table: New entry with `actor_user_id` = Patient A's ID, `owner_user_id` = Patient A's ID, `record_id` = RM_A2_ID, `action_type` = `'GRANT_ACCESS_SUCCESS'`, `target_address` = DOCTOR_X_BLOCKCHAIN_ADDRESS, and caller's IP address.
*   **Action 2: Patient A tries to grant access to RM_B1 (Patient B's record) to Doctor Y**
    1.  Log in as Patient A (get token).
    2.  Call API `POST /api/v1/medical-records/{RM_B1_ID}/grant-access` with Patient A's token and payload `{"doctor_address": "DOCTOR_Y_BLOCKCHAIN_ADDRESS"}`.
*   **Expected Result 2:**
    *   Failed response (403 Forbidden).
    *   Check `audit_data_access_logs` table: New entry with `actor_user_id` = Patient A's ID, `owner_user_id` = Patient A's ID (as Patient A is the actor, owner_user_id here is also Patient A's ID, not Patient B's, because the audit log records the action from `current_user`), `record_id` = RM_B1_ID, `action_type` = `'GRANT_ACCESS_FAILURE_FORBIDDEN'`.

### 3. Audit Log Verification for `revoke_medical_record_access` (Test Case 4.2.5)

*   **Preparation:**
    *   Patient A has a medical record (RM_A2) to which access has been granted to Doctor X.
*   **Action: Patient A revokes access to RM_A2 from Doctor X**
    1.  Log in as Patient A (get token).
    2.  Call API `POST /api/v1/medical-records/{RM_A2_ID}/revoke-access` with Patient A's token and payload `{"doctor_address": "DOCTOR_X_BLOCKCHAIN_ADDRESS"}`.
*   **Expected Result:**
    *   Successful response (200 OK).
    *   Check `audit_data_access_logs` table: New entry with `actor_user_id` = Patient A's ID, `owner_user_id` = Patient A's ID, `record_id` = RM_A2_ID, `action_type` = `'REVOKE_ACCESS_SUCCESS'`, `target_address` = DOCTOR_X_BLOCKCHAIN_ADDRESS, and caller's IP address.

### 4. Patient Access History API Verification (Test Case 4.2.6)

*   **Preparation:**
    *   Patient A has performed several actions resulting in audit logs (e.g., from tests 1, 2, and 3 above).
*   **Action:**
    1.  Log in as Patient A (get token).
    2.  Call API `GET /api/v1/audit/my-record-access-history` with Patient A's token.
*   **Expected Result:**
    *   Successful response (200 OK).
    *   Response body contains a list (array) of audit logs.
    *   Each entry in the list has `owner_user_id` equal to Patient A's ID.
    *   Verify that relevant logs from previous actions (e.g., `VIEW_RECORD_SUCCESS` by Patient A, `VIEW_RECORD_SUCCESS` by Doctor X, `GRANT_ACCESS_SUCCESS` by Patient A, `REVOKE_ACCESS_SUCCESS` by Patient A) appear in the list in reverse chronological order (newest first).
    *   Check `skip` and `limit` parameters for pagination functionality.

---
Jika ada masalah atau hasil yang tidak sesuai harapan, catat langkah-langkahnya, hasil yang didapat, dan hasil yang diharapkan untuk dilaporkan.

## Deployment Smart Contract (MedicalRecordRegistry.sol) ke Ganache (Lokal)

Setelah melakukan modifikasi pada `MedicalRecordRegistry.sol` dan tes unitnya berhasil, langkah berikutnya adalah men-deploy ulang _smart contract_ tersebut ke jaringan Ganache lokal Anda.

1.  **Pastikan Ganache Berjalan:**
    *   Pastikan instance Ganache Anda sudah berjalan dan dikonfigurasi sesuai dengan `hardhat.config.js` (biasanya di `http://127.0.0.1:8545` atau `http://127.0.0.1:7545` dengan `chainId: 1337`).
    *   Anda bisa menjalankan Ganache dengan perintah (sesuaikan `dbPath` jika perlu):
        ```bash
        ganache --deterministic --chain.chainId 1337 --database.dbPath ./.ganache-db
        ```

2.  **Navigasi ke Direktori Blockchain:**
    *   Buka terminal Anda dan navigasi ke direktori `blockchain` di dalam proyek Anda:
        ```bash
        cd path/to/your/project/blockchain
        ```

3.  **Jalankan Skrip Deployment:**
    *   Gunakan Hardhat untuk menjalankan skrip deployment. Skrip ini biasanya berada di direktori `scripts/` (misalnya, `deployMedicalRecordRegistry.js`).
        ```bash
        npx hardhat run scripts/deployMedicalRecordRegistry.js --network ganache
        ```
    *   **Catatan:** Jika Anda menjalankan perintah dari direktori root proyek, path ke skrip mungkin perlu disesuaikan (misalnya `blockchain/scripts/...`). Namun, instruksi di atas mengasumsikan Anda berada di dalam direktori `blockchain`.

4.  **Verifikasi Deployment:**
    *   Setelah deployment berhasil, Hardhat akan mencetak alamat kontrak yang baru di-deploy ke konsol.
    *   Pastikan file ABI (Application Binary Interface) dan alamat kontrak yang baru telah diperbarui di direktori `blockchain/build/deployments/`. File-file ini (biasanya `MedicalRecordRegistry.json` yang berisi ABI dan alamat di jaringan tertentu) sangat penting karena backend (`src/app/core/config.py`) akan membaca informasi ini untuk berinteraksi dengan kontrak.
    *   Jika `config.py` membaca dari path seperti `blockchain/build/deployments/ganache/MedicalRecordRegistry.json`, pastikan file tersebut ter-update dengan timestamp dan alamat terbaru.

5.  **Restart Backend Server (Jika Perlu):**
    *   Jika backend server Anda sudah berjalan, restart server tersebut agar ia memuat konfigurasi _smart contract_ yang baru (ABI dan alamat).
