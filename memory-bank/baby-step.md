# Baby Step To-Do List: MediTrustAl

*(Note: This file will be filled by Gemini or the Planning AI at each Vibe Coding cycle. The content below is an example if we follow the suggestion from `status-todolist-suggestions.md` above).*

## Current Baby-Step Context:
* **Parent Module:** Module 0: Environment Setup & Basic Infrastructure.
* **Objective of Baby-Step:** Formally initialize the project, set up version control, and connect it to a remote repository.

## Detailed Tasks for Current Baby-Step:

1.  **Task: Project Initialization & Version Control**
    * **Description:** Setting up the project's foundation on the local file system, initializing Git for version tracking, and linking it to an online repository for collaboration and backup.
    * **Sub-Tasks:**
        1.  **Create Main Project Folder Structure:**
            * **Instruction:** In your desired location on your local file system, create a main folder named `MediTrustAl_Project`.
            * **Validation:** Verify that the `MediTrustAl_Project` folder has been successfully created.
        2.  **Prepare `src` and `memory-bank` Folders:**
            * **Instruction:** Inside `MediTrustAl_Project`, create a subfolder named `src`. Copy the `memory-bank` folder, which already contains the planning documents (`product-design-document.md`, etc.), into `MediTrustAl_Project`.
            * **Validation:** Ensure `MediTrustAl_Project` now contains an empty `src` folder and the `memory-bank` folder (with all .md files inside).
        3.  **Initialize Git Repository:**
            * **Instruction:** Open your terminal or command prompt application. Navigate to the `MediTrustAl_Project` directory (e.g., `cd path/to/MediTrustAl_Project`). Run the command `git init`.
            * **Validation:** Check if a hidden `.git` folder is created inside `MediTrustAl_Project`. A confirmation message from `git init` usually also appears.
        4.  **Create and Configure `.gitignore` File:**
            * **Instruction:** Inside the `MediTrustAl_Project` folder, create a new file named `.gitignore`. Populate this file with common file and folder patterns to ignore for development projects (e.g., Python, Node.js, environment files). Example initial content:
                ```
                # Byte-compiled / optimized / DLL files
                __pycache__/
                *.py[cod]
                *$py.class

                # C extensions
                *.so

                # Distribution / packaging
                .Python
                build/
                develop-eggs/
                dist/
                downloads/
                eggs/
                .eggs/
                lib/
                lib64/
                parts/
                sdist/
                var/
                wheels/
                *.egg-info/
                .installed.cfg
                *.egg
                MANIFEST

                # PyInstaller
                #  Usually these files are written by a python script from a template
                #  before PyInstaller builds the exe, so as to inject date/other infos into it.
                *.manifest
                *.spec

                # Installer logs
                pip-log.txt
                pip-delete-this-directory.txt

                # Unit test / coverage reports
                htmlcov/
                .tox/
                .nox/
                .coverage
                .coverage.*
                .cache
                nosetests.xml
                coverage.xml
                *.cover
                .hypothesis/
                .pytest_cache/

                # Environments
                .env
                .venv
                env/
                venv/
                ENV/
                env.bak/
                venv.bak/

                # Spyder project settings
                .spyderproject
                .spyproject

                # Rope project settings
                .ropeproject

                # mkdocs documentation
                /site

                # Node.js
                node_modules/
                npm-debug.log*
                yarn-debug.log*
                yarn-error.log*
                package-lock.json
                yarn.lock

                # IDE / Editor specific
                .vscode/
                .idea/
                *.swp
                *.swo
                ```
            * **Validation:** The `.gitignore` file exists in the root of `MediTrustAl_Project` and contains relevant patterns.
        5.  **Create Remote Repository (e.g., on GitHub):**
            * **Instruction:** Open your browser and go to GitHub (or your preferred Git hosting platform). Create a new repository. Name it, for example, `MediTrustAl`. Choose whether it will be public or private. Do not initialize it with a README, .gitignore, or license from GitHub as we already have these.
            * **Validation:** The new repository is created on GitHub, and you have its remote URL (e.g., `https://github.com/USERNAME/MediTrustAl.git`).
        6.  **Connect Local Repository to Remote:**
            * **Instruction:** Return to your terminal (still inside the `MediTrustAl_Project` directory). Run the command: `git remote add origin YOUR_REMOTE_URL` (replace `YOUR_REMOTE_URL` with the URL you got from the previous step).
            * **Validation:** Run `git remote -v` to ensure the `origin` remote has been added correctly and points to the appropriate fetch & push URLs.
        7.  **Make Initial Commit:**
            * **Instruction:** In the terminal, run `git add .` to add all files in `MediTrustAl_Project` (that are not ignored by `.gitignore`) to the staging area. Then run `git commit -m "Initial project setup with Vibe Coding documents"`.
            * **Validation:** The `git status` command should show "nothing to commit, working tree clean". `git log` will display the first commit.
        8.  **Push Initial Commit to Remote:**
            * **Instruction:** In the terminal, run `git push -u origin main` (or `master` if that's your default branch name. If you are using `main` and your local default branch is `master`, you might need to run `git branch -M main` first before pushing).
            * **Validation:** Open your repository page on GitHub (or other platform). You should see all committed files and folders (including `memory-bank` and its contents) appearing there.

*(This file will be deleted or archived after all tasks within it are completed and validated, then the Planning AI will create the next baby-step).*