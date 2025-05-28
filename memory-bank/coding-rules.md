# **Cursor Rules for MediTrustAl Project (.mdc format draft)**

## **General Principles & Triggering**

* **Trigger:** These rules should generally trigger when generating or modifying code files related to the MediTrustAl project.  
* **Goal:** To ensure code is modular, maintainable, adheres to the chosen tech stack, and aligns with the project's design and architecture.  
* **Modularity Focus:** Prioritize creating multiple, well-defined files/modules over large, monolithic files. Each file should have a single, clear responsibility.

## **"Always" Rules (Critical for Context)**

These rules must be set to "Always" trigger in Cursor to ensure the AI always consults these documents before any code generation or modification task.

1. **Rule: Read Architecture Document**  
   * **Instruction:** "Always read memory-bank/architecture.md before writing or modifying any code. Pay close attention to the documented file structures, component responsibilities, and overall system design. If architecture.md is empty or does not cover the current task, state this and ask for clarification or instruct to proceed with creating a new architectural component description."  
   * **Context Files:** memory-bank/architecture.md  
2. **Rule: Read Product Requirements Document (PRD)**  
   * **Instruction:** "Always read memory-bank/product-design-document.md (equivalent to game-design-document.md) before writing or modifying any code. Ensure the code aligns with the project objectives, target users, and specified features. If the current task seems to deviate or is not covered, state this and ask for clarification."  
   * **Context Files:** memory-bank/product-design-document.md  
3. **Rule: Read Tech Stack Document**  
   * **Instruction:** "Always read memory-bank/tech-stack.md before writing or modifying any code. Ensure all code strictly adheres to the recommended technologies, libraries, frameworks, and patterns outlined in this document. Do not introduce new technologies without explicit instruction."  
   * **Context Files:** memory-bank/tech-stack.md

## **Modularity and Code Structure Rules**

These rules guide the AI in creating a well-structured and modular codebase.

4. **Rule: Emphasize File Modularity**  
   * **Instruction:** "When implementing features or components, break down the code into multiple, smaller, well-named files. Each file should have a single responsibility. Avoid creating overly long files. For example, for backend services, separate routes, controllers/handlers, services, and models/data access layers into different files/directories. For frontend, create separate component files."  
   * **Trigger:** When generating new features or significantly refactoring existing code.  
5. **Rule: Discourage Monolithic Files**  
   * **Instruction:** "If a file starts to exceed a reasonable length (e.g., more than 300-400 lines, depending on complexity and language), actively look for opportunities to refactor it into smaller, more focused modules or files. Propose this refactoring if appropriate."  
   * **Trigger:** When modifying existing files or adding substantial code to a single file.  
6. **Rule: Clear Naming Conventions**  
   * **Instruction:** "Use clear, descriptive, and consistent naming conventions for files, folders, variables, functions, classes, and components, following best practices for the specific language and framework being used (as per tech-stack.md)."  
   * **Trigger:** When generating any new code or identifiers.

## **Tech Stack Specific Rules (Examples \- to be expanded based on choices)**

These rules provide more specific guidance based on the chosen tech stack.

### **Blockchain (Hyperledger Fabric \- if chosen)**

**Panduan MVP (Ganache & Solidity):** Untuk pengembangan MVP, ikuti struktur dan praktik terbaik Solidity dengan Hardhat seperti yang telah diimplementasikan. Gunakan `MedicalRecordRegistry.sol` dan `UserRegistry.sol` sebagai acuan.

7. **Rule: Chaincode Structure**  
   * **Instruction:** "When developing Hyperledger Fabric chaincode (smart contracts), ensure a clear separation of concerns. For example, differentiate logic for different asset types or transactions. Follow recommended Fabric patterns for chaincode development (e.g., using the contract API)."  
   * **Context Files:** memory-bank/tech-stack.md  
   * **Trigger:** When generating or modifying chaincode.

### **NLP & AI Layer (Python)**

8. **Rule: Python Module Structure**  
   * **Instruction:** "For Python-based AI/NLP modules, organize code into logical packages and sub-modules. For instance, separate data preprocessing, model definition, training scripts, and inference/serving logic. Use \_\_init\_\_.py files appropriately."  
   * **Context Files:** memory-bank/tech-stack.md  
   * **Trigger:** When generating or modifying Python code for the AI/NLP layer.  
9. **Rule: API Design for AI Models**  
   * **Instruction:** "When exposing AI/NLP models via APIs (e.g., using FastAPI/Flask as per tech-stack.md), design clear, versioned, and well-documented API endpoints. Ensure request and response schemas are well-defined."  
   * **Context Files:** memory-bank/tech-stack.md  
   * **Trigger:** When creating or modifying API endpoints for AI/NLP models.

### **Application Layer (Node.js/Python Backend, React/Vue Frontend \- if chosen)**

10. **Rule: Backend Service Structure (e.g., Node.js with Express or Python with FastAPI/Django)**  
    * **Instruction:** "Structure backend services with clear separation for routes, controllers/handlers, business logic/services, and data access layers/models. Use middleware appropriately for concerns like authentication, logging, and error handling."  
    * **Context Files:** memory-bank/tech-stack.md  
    * **Trigger:** When generating or modifying backend code.  
11. **Rule: Frontend Component Structure (e.g., React/Vue)**  
    * **Instruction:** "Develop frontend UIs using a component-based architecture. Create small, reusable components. Separate presentational components from container/logic components where appropriate. Follow conventions for state management (e.g., Redux/Zustand for React, Vuex/Pinia for Vue) as outlined in tech-stack.md."  
    * **Context Files:** memory-bank/tech-stack.md  
    * **Trigger:** When generating or modifying frontend code.

## **General Coding Best Practices**

12. **Rule: Code Commenting and Documentation**  
    * **Instruction:** "Write clear and concise comments to explain complex logic, function purposes, and important decisions. For public APIs and complex functions, include docstrings or Javadoc-style comments. Aim for self-documenting code where possible, but do not shy away from comments where clarity is needed."  
    * **Trigger:** When generating any code.  
13. **Rule: Error Handling**  
    * **Instruction:** "Implement robust error handling. Use try-catch blocks appropriately. Log errors effectively. Provide meaningful error messages to users or calling services. Avoid failing silently."  
    * **Trigger:** When generating code that involves I/O, API calls, or complex logic.  
14. **Rule: Security Best Practices**  
    * **Instruction:** "Adhere to security best practices relevant to the language and framework. For example, prevent SQL injection, XSS, CSRF. Sanitize inputs. Follow guidelines in tech-stack.md regarding security measures like encryption and authentication."  
    * **Context Files:** memory-bank/tech-stack.md  
    * **Trigger:** When generating code that handles user input, data storage, or authentication/authorization.  
15. **Rule: Adherence to Interoperability Standards (HL7 FHIR)**  
    * **Instruction:** "When developing functionalities related to data exchange with external healthcare systems, strictly adhere to the HL7 FHIR standard as specified in tech-stack.md. Ensure FHIR resources are correctly structured and validated."  
    * **Context Files:** memory-bank/tech-stack.md  
    * **Trigger:** When generating code for data interoperability features.

## **Updating Architecture Document**

16. **Rule: Prompt to Update Architecture Document**  
    * **Instruction:** "After successfully implementing a major feature, a new service, or a significant architectural component, remind the user (developer) to update memory-bank/architecture.md to reflect these changes, including file purposes and interactions. This is crucial for maintaining an up-to-date architectural overview for future AI tasks."  
    * **Trigger:** After completing a significant coding task that alters or adds to the system's architecture.

This set of rules provides a solid starting point. You'll likely refine and add more specific rules as the project progresses and as you observe the AI's behavior in Cursor. Remember to mark rules 1, 2, and 3 as "Always" in your Cursor setup.