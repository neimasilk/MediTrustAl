# Baby Steps: Implementing Frontend Mockup-01 (Login) & Mockup-02 (Registration)

This document provides a step-by-step guide (baby steps) for implementing frontend functionality based on Mockup-01 (Login Page) and Mockup-02 (Registration Page). The goal is to eliminate ambiguity and simplify the development process for developers (especially juniors).

**Primary References:**
*   `frontend/mockups/mockup-01-login.html`
*   `frontend/mockups/mockup-02-register.html`
*   `memory-bank/outline-mockup.md` (for detailed specifications, if any)
*   `src/app/api/v1/endpoints/auth.py` (for Login & Registration API endpoint details)
*   `frontend/src/services/api.js` (or similar file for API interaction in the frontend)
*   `frontend/src/store/authSlice.js` (or similar file for authentication state management)

## A. General Frontend Preparation

Before starting the specific implementation for Login and Registration, ensure the following are already in place or created if not:

1.  **Component & Page Directory Structure:**
    *   Ensure there is a `frontend/src/pages` directory for page components (e.g., `LoginPage.jsx`, `RegisterPage.jsx`).
    *   Ensure there is a `frontend/src/components` directory for reusable UI components (e.g., `InputField.jsx`, `Button.jsx`, `Notification.jsx`).

2.  **Routing:**
    *   Basic routing configuration using `react-router-dom`.
    *   Create a route for `/login` pointing to `LoginPage`.
    *   Create a route for `/register` pointing to `RegisterPage`.
    *   Implement `PublicRoute` that redirects logged-in users from `/login` and `/register` to `/dashboard`.
    *   Implement `PrivateRoute` that redirects users not logged in from protected routes (e.g., `/dashboard`) to `/login`.

3.  **API Service:**
    *   Create or ensure there is a `frontend/src/services/api.js` file (or similar name) containing functions to make requests to the backend.
    *   Use `axios` or the `fetch` API.
    *   Configure the base URL for the backend API (e.g., `http://localhost:8000/api/v1`).
    *   Implement a `loginUser(credentials)` function that makes a `POST` request to `/auth/token`.
    *   Implement a `registerUser(userData)` function that makes a `POST` request to `/auth/register`.
    *   Include good error handling to catch error responses from the API.

4.  **State Management:**
    *   Use Redux Toolkit (or Context API if the project is smaller and agreed upon).
    *   Create an `authSlice` that will handle authentication-related state:
        *   `user`: null or user object if logged in.
        *   `token`: null or JWT token if logged in.
        *   `isLoading`: boolean (for loading indicator during login/register process).
        *   `error`: null or error message if an error occurs.
    *   Create reducers and actions for:
        *   `loginStart`, `loginSuccess`, `loginFailure`
        *   `registerStart`, `registerSuccess`, `registerFailure`
        *   `logout`
    *   Implement thunks (if using Redux Toolkit) to handle asynchronous login and registration logic that calls functions from `api.js` and dispatches the appropriate actions.

5.  **Token Utilities:**
    *   Create a utility file (e.g., `frontend/src/utils/tokenManager.js`) to save and retrieve JWT tokens from `localStorage`.
    *   Functions: `saveToken(token)`, `getToken()`, `removeToken()`.
    *   Ensure the `axios` (or `fetch`) instance is configured to include the JWT token in the `Authorization` header for requests requiring authentication.

6.  **Basic UI Components (Reusable Components):**
    *   Create basic components if they don't already exist:
        *   `InputField.jsx`: Generic input component with props for `type`, `placeholder`, `value`, `onChange`, `label`, `error`.
        *   `Button.jsx`: Generic button component with props for `text`, `onClick`, `type` (`submit`, `button`), `disabled`, `variant` (primary, secondary, etc.).
        *   `Notification.jsx`: Component for displaying notification messages (success, error, warning). Can use a library like `react-toastify` or create a custom one.
        *   `LoadingSpinner.jsx`: Component for loading indicator.

## B. Implementing Mockup-01: Login Page (`LoginPage.jsx`)

**Objective:** Create a login page that allows users to enter their username/email and password, send it to the backend, and handle the response.

**Target File:** `frontend/src/pages/LoginPage.jsx`

**Steps:**

1.  **`LoginPage.jsx` Component Structure:**
    *   Import React, `useState`, `useDispatch`, `useSelector` (from `react-redux`), `Link` (from `react-router-dom`), and the login thunk from `authSlice`.
    *   Import necessary UI components (`InputField`, `Button`, `Notification`, `LoadingSpinner`).
    *   Create local state using `useState` for input fields:
        *   `usernameOrEmail`
        *   `password`
    *   Use `useDispatch` to get the `dispatch` function.
    *   Use `useSelector` to get `isLoading` and `error` state from `authSlice`.

2.  **Layout and Styling (JSX & CSS):**
    *   Replicate the appearance from `mockup-01-login.html`.
    *   Use CSS Modules or styled-components for styling (according to project conventions).
    *   Ensure the page is responsive.
    *   Basic JSX structure:
        ```jsx
        <div className="login-container">
          <h2>Login to Account</h2>
          <form onSubmit={handleSubmit}>
            <InputField
              label="Username or Email"
              type="text" // or email if backend only accepts email for login
              value={usernameOrEmail}
              onChange={(e) => setUsernameOrEmail(e.target.value)}
              // Add error handling if any
            />
            <InputField
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              // Add error handling if any
            />
            {error && <Notification type="error" message={error} />}
            <Button type="submit" text="Login" disabled={isLoading} />
            {isLoading && <LoadingSpinner />}
          </form>
          <p>Don't have an account? <Link to="/register">Register here</Link></p>
        </div>
        ```

3.  **Handle Submit Logic (`handleSubmit`):**
    *   Create the `handleSubmit` function to be called on form submission.
    *   Call `event.preventDefault()`.
    *   Perform basic frontend input validation (optional, as the backend also validates, but good for UX):
        *   Ensure `usernameOrEmail` and `password` are not empty.
        *   If there's a validation error, display a message using the `Notification` component or local error state.
    *   If validation passes, dispatch the login thunk with `usernameOrEmail` and `password` as arguments:
        ```javascript
        dispatch(loginUserThunk({ username: usernameOrEmail, password })); 
        // Adjust payload to what backend /auth/token expects (usually form data: username & password)
        ```

4.  **Handling Login Result:**
    *   `authSlice` will handle the API response.
    *   If login is successful (`loginSuccess` is dispatched):
        *   Token and user data will be stored in Redux state.
        *   Token will be stored in `localStorage` (done within the thunk or reducer).
        *   The user will be redirected to `/dashboard`. Use `useNavigate` from `react-router-dom` or do this within the thunk after success.
    *   If login fails (`loginFailure` is dispatched):
        *   The error message from the backend will be stored in Redux state (`error`).
        *   The `Notification` component will display this error message.

5.  **Loading Indicator:**
    *   The "Login" button should be disabled when `isLoading` is `true`.
    *   Display the `LoadingSpinner` component when `isLoading` is `true`.

6.  **Link to Registration Page:**
    *   Ensure there is a link to `/register` for users who don't have an account.

7.  **Initial Manual Testing:**
    *   Run the frontend and backend.
    *   Try logging in with incorrect credentials, ensure an error message appears.
    *   Try logging in with correct credentials, ensure redirection to the dashboard (if it exists) or another appropriate page.
    *   Check `localStorage` for the JWT token after successful login.
    *   Check Redux DevTools to see state changes.

## C. Implementing Mockup-02: Registration Page (`RegisterPage.jsx`)

**Objective:** Create a registration page that allows new users to sign up by filling in the required data, sending it to the backend, and handling the response.

**Target File:** `frontend/src/pages/RegisterPage.jsx`

**Steps:**

1.  **`RegisterPage.jsx` Component Structure:**
    *   Similar to `LoginPage.jsx`: import React, hooks, actions, UI components.
    *   Local state for registration input fields (align with `UserCreate` schema in backend `src/app/schemas/user.py` and `mockup-02-register.html`):
        *   `email`
        *   `username`
        *   `full_name`
        *   `password`
        *   `confirmPassword` (for frontend validation)
        *   `role` (if user-selectable, defaults to 'patient')
        *   `blockchain_address` (optional during registration, or auto-generate if designed that way)
    *   Use `useSelector` for `isLoading` and `error` from `authSlice`.

2.  **Layout and Styling (JSX & CSS):**
    *   Replicate the appearance from `mockup-02-register.html`.
    *   Ensure the page is responsive.
    *   Basic JSX structure (example, adjust fields accordingly):
        ```jsx
        <div className="register-container">
          <h2>Create New Account</h2>
          <form onSubmit={handleSubmit}>
            <InputField label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <InputField label="Username" type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
            <InputField label="Full Name" type="text" value={full_name} onChange={(e) => setFullName(e.target.value)} />
            <InputField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <InputField label="Confirm Password" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
            {/* Add other fields if any, e.g., Role, Blockchain Address */} 
            {error && <Notification type="error" message={error} />}
            <Button type="submit" text="Register" disabled={isLoading} />
            {isLoading && <LoadingSpinner />}
          </form>
          <p>Already have an account? <Link to="/login">Login here</Link></p>
        </div>
        ```

3.  **Handle Submit Logic (`handleSubmit`):**
    *   Create the `handleSubmit` function.
    *   Call `event.preventDefault()`.
    *   Perform frontend input validation:
        *   All required fields must be filled (except optional ones).
        *   Valid email format.
        *   Password and `confirmPassword` must match.
        *   Minimum password length (if there are rules).
        *   If there's a validation error, display a message.
    *   If validation passes, create a `userData` object to be sent to the backend (according to `UserCreate` schema):
        ```javascript
        const userData = { email, username, full_name, password, role: 'patient' /*, blockchain_address */ };
        ```
    *   Dispatch the registration thunk:
        ```javascript
        dispatch(registerUserThunk(userData));
        ```

4.  **Handling Registration Result:**
    *   `authSlice` will handle the API response.
    *   If registration is successful (`registerSuccess` is dispatched):
        *   Display a success message (e.g., "Registration successful! Please login.").
        *   Redirect the user to the `/login` page (or auto-login if designed that way, but usually to login first).
    *   If registration fails (`registerFailure` is dispatched):
        *   Error messages from the backend (e.g., "Username already exists", "Email already registered") will be stored in Redux state (`error`).
        *   The `Notification` component will display this error message.

5.  **Loading Indicator:**
    *   Same as in `LoginPage.jsx`.

6.  **Link to Login Page:**
    *   Ensure there is a link to `/login` for users who already have an account.

7.  **Initial Manual Testing:**
    *   Run the frontend and backend.
    *   Try registering with valid data. Ensure success and redirection to login.
    *   Try registering with an existing username or email. Ensure appropriate error messages appear.
    *   Try registering with mismatched password and confirm password. Ensure frontend validation error appears.
    *   Check the database to ensure the new user is saved correctly after successful registration.
    *   Check Redux DevTools.

## D. Next Steps After Initial Implementation

1.  **Refinement & Advanced Styling:**
    *   Ensure styling perfectly matches the HTML mockups.
    *   Pay attention to UX details like clear error messages and feedback on interaction.

2.  **More Detailed Error Handling:**
    *   Handle various types of errors from the backend (400, 401, 403, 409, 500) with more specific messages if possible.

3.  **Integration with Other Components:**
    *   Ensure the navigation flow after login/registration works smoothly to the dashboard or other relevant pages.

4.  **Writing Unit Tests (if at that stage):**
    *   Write unit tests for `LoginPage` and `RegisterPage` components.
    *   Write unit tests for `authSlice` (reducers, actions, thunks).

5.  **Review and Iteration:**
    *   Conduct code reviews.
    *   Test manually again to ensure all scenarios are handled well.

By following these steps, the implementation of the Login and Registration pages is expected to be more structured and less ambiguous.