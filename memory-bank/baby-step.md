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
            * **Instruction:** *(Tidak relevan jika Anda sudah berada di root repositori GitHub Anda.)*
            * **Validation:** *(Tidak relevan jika Anda sudah berada di root repositori GitHub Anda.)*
        2.  **Prepare `src` and `memory-bank` Folders:**
            * **Instruction:** Di dalam root repositori Anda, buat subfolder `src`. Salin folder `memory-bank` yang ada ke dalam root repositori Anda.
            * **Validation:** Pastikan root repositori Anda sekarang berisi folder `src` (awalnya kosong) dan folder `memory-bank` (dengan semua file .md di dalamnya).
        3.  **Initialize Git Repository:**
            * **Instruction:** *(Langkah ini kemungkinan sudah selesai jika Anda mengkloning repositori yang ada. Jika tidak, buka terminal atau command prompt Anda, navigasikan ke root repositori Anda, lalu jalankan perintah `git init`.)*
            * **Validation:** Periksa apakah folder `.git` yang tersembunyi ada di dalam root repositori Anda. Pesan konfirmasi dari `git init` biasanya juga muncul.
        4.  **Create and Configure `.gitignore` File:**
            * **Instruction:** Di dalam root repositori Anda, buat file `.gitignore`. Anda dapat mengisi file ini nanti dengan pola file dan folder umum yang akan diabaikan untuk proyek pengembangan (misalnya, Python, Node.js, file lingkungan).
            * **Validation:** File `.gitignore` ada di root repositori Anda.
        5.  **Create Remote Repository (e.g., on GitHub):**
            * **Instruction:** *(Langkah ini kemungkinan sudah selesai jika Anda mengkloning repositori yang ada.)* Open your browser and go to GitHub (or your preferred Git hosting platform). Create a new repository if you haven't already. Name it. Choose whether it will be public or private. Do not initialize it with a README, .gitignore, or license from GitHub if you are creating it now and already have these locally.
            * **Validation:** The new repository is created on GitHub, and you have its remote URL (e.g., `https://github.com/USERNAME/MediTrustAl.git`).
        6.  **Connect Local Repository to Remote:**
            * **Instruction:** *(Lakukan ini jika Anda menginisialisasi repositori secara lokal dan belum menghubungkannya ke remote).* Return to your terminal (pastikan Anda berada di root repositori Anda). Run the command: `git remote add origin YOUR_REMOTE_URL` (replace `YOUR_REMOTE_URL` with the URL you got from the previous step).
            * **Validation:** Run `git remote -v` to ensure the `origin` remote has been added correctly and points to the appropriate fetch & push URLs.
        7.  **Make Initial Commit:**
            * **Instruction:** In the terminal (at your repository root), run `git add .` to add all files in your repository (that are not ignored by `.gitignore`) to the staging area. Then run `git commit -m "Initial project setup with Vibe Coding documents"`.
            * **Validation:** The `git status` command should show "nothing to commit, working tree clean" (or show untracked files if you haven't added everything). `git log` will display the first commit.
        8.  **Push Initial Commit to Remote:**
            * **Instruction:** In the terminal (at your repository root), run `git push -u origin main` (or `master` if that's your default branch name. If you are using `main` and your local default branch is `master`, you might need to run `git branch -M main` first before pushing).
            * **Validation:** Open your repository page on GitHub (or other platform). You should see all committed files and folders (including `memory-bank` and its contents) appearing there.

*(This file will be deleted or archived after all tasks within it are completed and validated, then the Planning AI will create the next baby-step).*