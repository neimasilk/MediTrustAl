# MediTrustAl Frontend Mockup Outline

This document outlines the frontend mockups for client presentation. The primary focus is on patient and doctor user flows, highlighting security and data management features.

## A. General User Flow (Public)

* [x] **M01: Login Page (`mockup-01-login.html`)**
    * Fields: Username/Email, Password
    * Buttons: Login
    * Links: "Don't have an account? Sign Up", "Forgot Password?"
    * Displays error messages on login failure.
* [x] **M02: Registration Page (`mockup-02-register.html`)**
    * Fields: Username, Email, Full Name, Password, Confirm Password, Role (Dropdown: Patient, Doctor)
    * Buttons: Register
    * Links: "Already have an account? Login"
    * Displays validation error messages or registration success (redirecting to login).

## B. Patient User Flow (After Login)

* [x] **M03: Patient Dashboard (`mockup-03-patient-dashboard.html`)**
    * Header: User Name, Logout Button.
    * Main Summary/Widgets: Potentially important notifications or brief health data (placeholders).
    * **My Medical Records List:**
        * Table/List: Record ID, Record Type, Date Created, Data Hash (shortened), "Manage Access" Button.
        * Message if no medical records exist.
        * "Create New Medical Record" Button (leads to M04 or a modal).
    * **My Data Access History (Summary):**
        * Table/List (Brief): Date, Accessed By (Doctor/Yourself), Action Type, Related Record ID.
        * Link "View Full Access History" (leads to M05).
    * Navigation (Sidebar/Menu): Dashboard, My Medical Records, Consent Management, Access History, Profile.
* [x] **M04: Create New Medical Record Page/Modal (Patient) (`mockup-04-patient-create-record.html`)**
    * Fields: Record Type (Dropdown), Metadata (JSON or dynamic fields based on type), Raw Data Input (Textarea).
    * Buttons: Save, Cancel.
* [x] **M05: Patient Data Access History Detail Page (`mockup-05-patient-audit-log.html`)**
    * Filters: By Date, Action Type.
    * Detailed Table: Timestamp, Actor (User ID/Name), Target Record (ID), Action Type, IP Address, Additional Details (if any).
    * Pagination.
* [x] **M06: Manage Medical Record Access Modal (Patient) (`mockup-06-patient-manage-access-modal.html`)**
    * Displayed when "Manage Access" button on the dashboard is clicked.
    * Record Info: ID, Type, Hash.
    * Input field: Doctor's Blockchain Address.
    * Buttons: "Grant Access", "Revoke Access".
    * List of Doctors Currently Having Access (Name/Address, Date Granted).
    * Feedback messages (success/error).

## C. Doctor User Flow (After Login)

* [x] **M07: Doctor Dashboard (`mockup-07-doctor-dashboard.html`)**
    * Header: Doctor Name, Logout Button.
    * Patient Search (by DID or Name).
    * List of Recently Accessed Patients or Patients with Granted Access.
    * Navigation: Dashboard, Search Patient, Accessed Medical Records.
* [x] **M08: Patient Detail Page (for Doctor) (`mockup-08-doctor-patient-detail.html`)**
    * Patient Info (from DID/Blockchain).
    * List of Patient's Medical Records to which this Doctor has Access:
        * Table/List: Record ID, Type, Date, "View Record Details" Button.
* [x] **M09: Medical Record Detail Page (for Doctor) (`mockup-09-doctor-record-detail.html`)**
    * Displays decrypted medical record data (after successful access verification).
    * Metadata Information.
    * (Future) Display of NLP/AI analysis results related to this record.

## D. Common Components

* [x] **M10: Notification/Alert Display (`mockup-10-notifications.html`)**
    * Examples for success, error, warning, info messages.
* [x] **M11: User Profile Page (`mockup-11-user-profile.html`)**
    * Displays user information (Email, Username, Full Name, Role, DID, Blockchain Address).
    * (Future) Options to edit profile, change password.

---
*Checkboxes indicate that the outline item has been created, not necessarily the HTML mockup itself.*