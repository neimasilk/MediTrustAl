# Project Status, To-Do List, and Baby-Step Suggestions: MediTrustAl

## Current Project Status:
* **Project Phase:** Phase 1 - Core Backend Setup & Blockchain Foundation (MVP Focus).
* **Description:** Step 1.1 dari Rencana Implementasi MVP telah selesai. Struktur proyek dasar, backend FastAPI dengan endpoint status, serta konfigurasi awal untuk linting dan formatting telah disiapkan. Kode sumber awal telah di-commit ke version control.
* **Last Completed Step:** Module 0: Environment Setup & Basic Infrastructure - Step 1.1: Project Setup and Basic Backend Structure.

## General To-Do List (Based on `implementation-plan.md` for MVP):

1.  **Module 0: Environment Setup & Basic Infrastructure**
    * [x] Step 1.1: Project Setup and Basic Backend Structure
    * [ ] Step 1.2: Basic Blockchain Network Setup (Local Development)
    * [ ] Step 1.3: User Identity and Basic Authentication (Application Layer)
    * [ ] Initial Database Setup (PostgreSQL direkomendasikan, akan menjadi bagian dari Step 1.3 atau sebagai sub-task khusus)
2.  **Module 1: Patient Data Management - MVP Core (Blockchain Interaction)**
    * [ ] Step 2.1: Basic Patient Health Record (PHR) Structure on Blockchain
    * [ ] Step 2.2: Basic Off-Chain Data Storage Setup
    * [ ] Step 2.3: Basic Patient Data Retrieval
3.  **Module 2: Basic NLP & AI Placeholder and Frontend Shell**
    * [ ] Step 3.1: Placeholder NLP Service
    * [ ] Step 3.2: Placeholder AI Predictive Service
    * [ ] Step 3.3: Basic Frontend Shell (Patient Portal)
4.  **Module 3: Basic Consent Mechanism (Simplified for MVP)**
    * [ ] Step 4.1: Simplified Consent Logic in Chaincode
5.  **Module 4 (Tambahan dari `status-todolist-suggestions.md` sebelumnya, bisa diintegrasikan atau ditinjau ulang): Initial NLP Module Development**
    * [ ] Collection & Preprocessing of Sample Mandarin Narrative Medical Data
    * [ ] Implementation of Named Entity Recognition (NER) for Basic Entities
    * [ ] Development of Basic De-identification Function
    * [ ] Initial Terminology Standardization
6.  **Module 5 (Tambahan dari `status-todolist-suggestions.md` sebelumnya): Initial Predictive AI Model Development**
    * [ ] Use Case Definition & Data Collection
    * [ ] Feature Selection (Feature Engineering)
    * [ ] Implementation of Initial Classic Machine Learning Model
    * [ ] Creation of a Simple API for Predictions
7.  **Module 6 (Tambahan dari `status-todolist-suggestions.md` sebelumnya): Initial Integration & End-to-End MVP Testing**
    * [ ] NLP Integration with Data Storage & Blockchain
    * [ ] AI Integration with Doctor Portal & Patient Data
    * [ ] Testing of Core User Scenarios
    * [ ] Collection of Initial Feedback

## Suggested "Baby-Step To-Do List" for Next Step:

* **Current Focus:** Melanjutkan Module 0: Environment Setup & Basic Infrastructure.
* **Next Step:** **Step 1.2: Basic Blockchain Network Setup (Local Development)**
* **Suggested Baby-Step Tasks:**
    1.  **Task: Pemilihan Platform Blockchain (Konfirmasi)**
        * **Deskripsi:** Meskipun Hyperledger Fabric direkomendasikan, konfirmasikan pilihan final untuk pengembangan lokal MVP. Untuk kemudahan pengembangan lokal awal, Ganache (untuk chain berbasis Ethereum seperti Quorum yang disederhanakan) bisa dipertimbangkan sebelum migrasi penuh ke Fabric.
        * **Sub-Tasks:**
            1.  Buat keputusan platform blockchain untuk development lokal awal (misalnya, Ganache untuk simplicitas, atau Dockerized Fabric test network).
            2.  Dokumentasikan keputusan ini jika ada perubahan dari `tech-stack.md`.
        * **Validation:** Keputusan platform blockchain untuk dev lokal terdokumentasi.
    2.  **Task: Instalasi dan Setup Jaringan Blockchain Lokal**
        * **Deskripsi:** Menginstal dan mengkonfigurasi instance pengembangan lokal dari platform blockchain yang dipilih.
        * **Sub-Tasks:**
            1.  Instal perangkat lunak blockchain yang diperlukan (misalnya, Ganache UI/CLI, atau Docker images untuk Hyperledger Fabric).
            2.  Inisialisasi jaringan blockchain lokal (misalnya, buat workspace baru di Ganache, atau jalankan skrip untuk memulai Fabric test network).
            3.  Pastikan jaringan berjalan dan dapat diakses dari lingkungan pengembangan Anda.
        * **Validation:** Jaringan blockchain lokal berhasil dijalankan dan dapat diakses (misalnya, endpoint RPC terekspos, peers di Fabric terhubung).
    3.  **Task: Pengembangan Chaincode/Smart Contract Dasar untuk Registrasi "User"**
        * **Deskripsi:** Membuat chaincode/smart contract yang sangat dasar untuk mendaftarkan entitas "User" dengan ID unik dan peran (misalnya, "PATIENT", "DOCTOR").
        * **Sub-Tasks:**
            1.  Buat struktur proyek untuk chaincode/smart contract (misalnya, folder `chaincode/user_management/`).
            2.  Implementasikan fungsi dasar `registerUser(userId, userRole)` dalam bahasa smart contract yang relevan (misalnya, Go atau Node.js untuk Fabric, Solidity untuk Ganache/Ethereum).
            3.  (Opsional, tapi direkomendasikan) Implementasikan fungsi dasar `queryUser(userId)` untuk verifikasi.
        * **Validation:** Kode chaincode/smart contract dasar telah ditulis dan tidak ada error kompilasi (jika berlaku).
    4.  **Task: Deployment Chaincode/Smart Contract ke Jaringan Lokal**
        * **Deskripsi:** Mendemonstrasikan chaincode/smart contract ke jaringan blockchain lokal yang telah disiapkan.
        * **Sub-Tasks:**
            1.  Gunakan tools atau skrip yang sesuai dengan platform blockchain untuk mendeploy chaincode/smart contract (misalnya, `peer chaincode deploy` untuk Fabric, Truffle/Hardhat deploy scripts untuk Ethereum).
            2.  Catat alamat kontrak atau ID chaincode setelah deployment berhasil.
        * **Validation:** Chaincode/smart contract berhasil dideploy ke jaringan lokal dan ID/alamatnya diketahui.
    5.  **Task: Pengembangan Service Backend Awal untuk Interaksi Blockchain**
        * **Deskripsi:** Membuat service sederhana di dalam backend FastAPI untuk terhubung ke jaringan blockchain lokal dan memanggil transaksi `registerUser`.
        * **Sub-Tasks:**
            1.  Tambahkan library klien blockchain yang diperlukan ke `requirements.txt` (misalnya, `web3.py` untuk Ethereum, `fabric-sdk-py` untuk Fabric).
            2.  Buat modul baru di backend (misalnya, `src/app/blockchain_services/user_service.py`).
            3.  Implementasikan fungsi koneksi ke jaringan blockchain lokal.
            4.  Implementasikan fungsi untuk memanggil `registerUser` pada chaincode/smart contract yang telah dideploy.
            5.  (Opsional) Buat endpoint API internal sementara di FastAPI untuk memicu registrasi user via blockchain untuk testing.
        * **Validation:** Service backend dapat terhubung ke jaringan blockchain. Fungsi `registerUser` dapat dipanggil dari backend, menghasilkan transaksi yang berhasil di blockchain (dapat diverifikasi dengan query manual ke blockchain atau log).

*(Note: This file will be updated by Gemini or the Planning AI at each Vibe Coding cycle)*