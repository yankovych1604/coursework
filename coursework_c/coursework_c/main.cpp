#include <iostream>
#include <cstring>
#include <sstream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <sql.h>
#include <sqlext.h>
#include <vector>

#define LOGIN_PORT 8080
#define ADMIN_PORT 8081
#define BUFFER_SIZE 1024

using namespace std;

class Person {
protected:
    int id;
    string firstName;
    string lastName;
    string middleName;
public:
    Person(int id, const string &firstName, const string &lastName, const string &middleName) : id(id), firstName(firstName), lastName(lastName), middleName(middleName) {}
    
    virtual ~Person() = default;
    virtual string getRole() const = 0;
};

class Patient : public Person {
private:
    string birthDate;
    string contact;
public:
    Patient(int id, const string &firstName, const string &lastName, const string &middleName, const string &birthDate, const string &contact) : Person(id, firstName, lastName, middleName), birthDate(birthDate), contact(contact) {}
    
    string getRole() const override {
        return "PATIENT";
    }
    
    string toString() const {
        stringstream ss;
        ss << id << "|" << firstName << "|" << lastName << "|" << middleName << "|" << birthDate << "|" << contact;
        return ss.str();
    }
};

class PatientVisit : public Patient {
private:
    string visit_date;
    string visit_time;
    string doctor_name;
    string diagnosis;
    string treatment;
public:
    PatientVisit(int id, const string& firstName, const string& lastName, const string& middleName, const string& birthDate, const string& contact, const string& visitDate, const string& visitTime, const string& doctorName, const string& diagnosis, const string& treatment) : Patient(id, firstName, lastName, middleName, birthDate, contact), visit_date(visitDate), visit_time(visitTime), doctor_name(doctorName), diagnosis(diagnosis), treatment(treatment) {}

    string toString() const {
        return Patient::toString() + "|" + visit_date + "|" + visit_time + "|" + doctor_name + "|" + diagnosis + "|" + treatment;
    }
};

class DoctorSlot {
private:
    int id;
    string doctorName;
    string workDate;
    string startTime;
public:
    DoctorSlot(int id, const string &doctorName, const string &workDate, const string &startTime) : id(id), doctorName(doctorName), workDate(workDate), startTime(startTime) {}

    string toString() const {
        stringstream ss;
        ss << id << "|" << doctorName << "|" << workDate << "|" + startTime;
        return ss.str();
    }
};

class DatabaseManager {
private:
    SQLHENV env;
    SQLHDBC dbc;
public:
    DatabaseManager() {
        SQLAllocHandle(SQL_HANDLE_ENV, SQL_NULL_HANDLE, &env);
        SQLSetEnvAttr(env, SQL_ATTR_ODBC_VERSION, (SQLPOINTER)SQL_OV_ODBC3, 0);
        SQLAllocHandle(SQL_HANDLE_DBC, env, &dbc);
    }

    ~DatabaseManager() {
        SQLDisconnect(dbc);
        SQLFreeHandle(SQL_HANDLE_DBC, dbc);
        SQLFreeHandle(SQL_HANDLE_ENV, env);
    }

    SQLHDBC getConnection() const {
        return dbc;
    }
    
    void beginTransaction() {
        executeSQL("BEGIN TRANSACTION;", {});
    }

    void commitTransaction() {
        executeSQL("COMMIT;", {});
    }

    void rollbackTransaction() {
        executeSQL("ROLLBACK;", {});
    }
    
    bool connect(const string &dbName, const string &user, const string &password) {
        return SQL_SUCCEEDED(SQLConnect(dbc, (SQLCHAR*)dbName.c_str(), SQL_NTS, (SQLCHAR*)user.c_str(), SQL_NTS, (SQLCHAR*)password.c_str(), SQL_NTS));
    }
    
    SQLHSTMT prepareStatement(const string &query, const vector<string> &params) const {
        SQLHSTMT stmt;
        SQLAllocHandle(SQL_HANDLE_STMT, dbc, &stmt);

        for (size_t i = 0; i < params.size(); ++i) {
            SQLBindParameter(stmt, i + 1, SQL_PARAM_INPUT, SQL_C_CHAR, SQL_VARCHAR, 50, 0, (SQLCHAR*)params[i].c_str(), 0, nullptr);
        }
        if (!SQL_SUCCEEDED(SQLExecDirect(stmt, (SQLCHAR*)query.c_str(), SQL_NTS))) {
            SQLFreeHandle(SQL_HANDLE_STMT, stmt);
            return nullptr;
        }
        return stmt;
    }

    bool executeSQL(const string &query, const vector<string> &params, bool fetch = false) const {
        SQLHSTMT stmt = prepareStatement(query, params);
        if (!stmt) return false;

        bool success = (fetch) ? SQLFetch(stmt) == SQL_SUCCESS : true;
        SQLFreeHandle(SQL_HANDLE_STMT, stmt);
        return success;
    }

    vector<vector<string>> executeSQLWithResults(const string &query, const vector<string> &params, int expectedCols = -1) const {
        vector<vector<string>> results;
        SQLHSTMT stmt = prepareStatement(query, params);
        if (!stmt) return results;

        while (SQLFetch(stmt) == SQL_SUCCESS) {
            vector<string> row;
            SQLCHAR buffer[256];
            for (int i = 1; i <= expectedCols; ++i) {
                SQLGetData(stmt, i, SQL_C_CHAR, buffer, sizeof(buffer), nullptr);
                row.emplace_back(reinterpret_cast<char*>(buffer));
            }
            results.push_back(row);
        }
        SQLFreeHandle(SQL_HANDLE_STMT, stmt);
        return results;
    }
};

class Admin : public Person {
private:
    string login;
    string password;
public:
    Admin(int id, const string &firstName, const string &lastName, const string &middleName, const string &login, const string &password) : Person(id, firstName, lastName, middleName), login(login), password(password) {}


    string getRole() const override {
        return "ADMIN";
    }

    bool isPatientExists(DatabaseManager &dbManager, const string &firstName, const string &lastName, const string &middleName, const string &birthDate, const string &contact) {
        string query = "SELECT 1 FROM Patients WHERE first_name = ? AND last_name = ? AND middle_name = ? AND birth_date = ? AND contact = ?";
        
        return dbManager.executeSQL(query, {firstName, lastName, middleName, birthDate, contact}, true);
    }
    
    bool isDoctorExists(DatabaseManager &dbManager, const string &firstName, const string &lastName, const string &middleName) {
        string query = "SELECT 1 FROM Doctors WHERE first_name = ? AND last_name = ? AND middle_name = ?";
        
        return dbManager.executeSQL(query, {firstName, lastName, middleName}, true);
    }

    Patient addPatient(DatabaseManager &dbManager, const string &firstName, const string &lastName, const string &middleName, const string &birthDate, const string &contact) {
        if (isPatientExists(dbManager, firstName, lastName, middleName, birthDate, contact)) {
            throw runtime_error("EXISTS");
        }
        
        string insertQuery = "INSERT INTO Patients (first_name, last_name, middle_name, birth_date, contact) VALUES (?, ?, ?, ?, ?)";
        dbManager.executeSQL(insertQuery, {firstName, lastName, middleName, birthDate, contact});

        // Повертаємо щойно доданого пацієнта
        string selectQuery = "SELECT patient_id, first_name, last_name, middle_name, birth_date, contact FROM Patients "
                             "WHERE first_name = ? AND last_name = ? AND middle_name = ? AND birth_date = ? AND contact = ?";
        
        auto results = dbManager.executeSQLWithResults(selectQuery, {firstName, lastName, middleName, birthDate, contact}, 6);

        if (!results.empty()) {
            return Patient(stoi(results[0][0]), results[0][1], results[0][2], results[0][3], results[0][4], results[0][5]);
        } else {
            throw runtime_error("ERROR");
        }
    }

    bool deletePatient(DatabaseManager &dbManager, const string &firstName, const string &lastName, const string &middleName, const string &birthDate, const string &contact) {
        if (!isPatientExists(dbManager, firstName, lastName, middleName, birthDate, contact)) {
            return false;
        }
        
        string query = "DELETE FROM Patients WHERE first_name = ? AND last_name = ? AND middle_name = ? AND birth_date = ? AND contact = ?";
        
        return dbManager.executeSQL(query, {firstName, lastName, middleName, birthDate, contact});
    }

    Patient searchPatient(DatabaseManager &dbManager, const string &firstName, const string &lastName, const string &middleName, const string &birthDate, const string &contact) {
        string query = "SELECT patient_id, first_name, last_name, middle_name, birth_date, contact FROM Patients "
                       "WHERE first_name = ? AND last_name = ? AND middle_name = ? AND birth_date = ? AND contact = ?";
        
        auto results = dbManager.executeSQLWithResults(query, {firstName, lastName, middleName, birthDate, contact}, 6);

        if (!results.empty()) {
            return Patient(stoi(results[0][0]), results[0][1], results[0][2], results[0][3], results[0][4], results[0][5]);
        } else {
            throw runtime_error("NOT_FOUND");
        }
    }
    
    vector<Patient> getAllPatients(DatabaseManager &dbManager) {
        vector<Patient> patients;

        string query = "SELECT patient_id, first_name, last_name, middle_name, birth_date, contact FROM Patients";
        auto results = dbManager.executeSQLWithResults(query, {}, 6);

        for (const auto& row : results) {
            if (!row[0].empty()) {
                patients.emplace_back(stoi(row[0]), row[1], row[2], row[3], row[4], row[5]);
            }
        }

        return patients;
    }
    
    vector<PatientVisit> getPatientVisits(DatabaseManager &dbManager, int patient_id) {
        vector<PatientVisit> visits;

        string query = "SELECT p.patient_id, p.first_name, p.last_name, p.middle_name, p.birth_date, p.contact, ws.work_date, ws.start_time, d.last_name + ' ' + d.first_name + ' ' + d.middle_name AS doctor_name, COALESCE(diag.diagnosis, '') AS diagnosis, COALESCE(diag.treatment, '') AS treatment FROM Patients p JOIN Appointments a ON p.patient_id = a.patient_id JOIN WorkSlots ws ON a.slot_id = ws.slot_id JOIN Doctors d ON ws.doctor_id = d.doctor_id LEFT JOIN Diagnosis diag ON a.appointment_id = diag.appointment_id WHERE p.patient_id = ? ORDER BY ws.work_date DESC, ws.start_time DESC;";

        auto results = dbManager.executeSQLWithResults(query, {to_string(patient_id)}, 11);

        for (auto& row : results) {
            if (!row[0].empty() && !row[1].empty() && !row[2].empty() && !row[4].empty()) {
                visits.emplace_back(stoi(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]);
            }
        }

        return visits;
    }
    
    vector<DoctorSlot> getAvailableDoctorSlotsForDay(DatabaseManager &dbManager, const string &doctorFirstName, const string &doctorLastName, const string &doctorMiddleName, const string &date) {
        vector<DoctorSlot> slots;

        string query = "SELECT ws.slot_id, ws.work_date, ws.start_time, d.last_name + ' ' + LEFT(d.first_name, 1) + '.' + ' ' + LEFT(d.middle_name, 1) + '.' AS doctor_name FROM WorkSlots ws JOIN Doctors d ON ws.doctor_id = d.doctor_id WHERE d.first_name = ? AND d.last_name = ? AND ISNULL(d.middle_name, '') = ? AND ws.work_date = ? AND NOT EXISTS (SELECT 1 FROM Appointments a WHERE a.slot_id = ws.slot_id) AND (ws.work_date != CAST(GETDATE() AS DATE) OR (ws.work_date = CAST(GETDATE() AS DATE) AND DATEPART(HOUR, ws.start_time) >= DATEPART(HOUR, GETDATE()))) ORDER BY ws.start_time ASC;";

        auto results = dbManager.executeSQLWithResults(query, {doctorFirstName, doctorLastName, doctorMiddleName, date}, 4);

        for (const auto &row : results) {
            if (!row[0].empty() && !row[1].empty() && !row[2].empty() && !row[3].empty()) {
                slots.emplace_back(stoi(row[0]), row[1], row[2], row[3]);
            }
        }

        return slots;
    }
    
    bool bookAppointment(DatabaseManager &dbManager, int slot_id, const string &first_name, const string &last_name, const string &middle_name, const string &birth_date, const string &contact) {
        string checkQuery = "SELECT 1 FROM Appointments WHERE slot_id = ?";
        auto checkResult = dbManager.executeSQLWithResults(checkQuery, {to_string(slot_id)}, 1);

        if (!checkResult.empty()) {
            return false;
        }

        string patientQuery = "SELECT patient_id FROM Patients WHERE first_name = ? AND last_name = ? AND middle_name = ? AND birth_date = ? AND contact = ?";
        auto patientResult = dbManager.executeSQLWithResults(patientQuery, {first_name, last_name, middle_name, birth_date, contact}, 1);

        if (patientResult.empty()) {
            throw runtime_error("Пацієнт не знайдений");
        }

        string patient_id = patientResult[0][0];

        string insertQuery = "INSERT INTO Appointments (patient_id, slot_id, is_completed) VALUES (?, ?, 0)";
        dbManager.executeSQL(insertQuery, {patient_id, to_string(slot_id)});

        return true;
    }
    
    vector<PatientVisit> getPatientAppointments(DatabaseManager &dbManager, const string &firstName, const string &lastName, const string &middleName, const string &birthDate, const string &contact) {
        vector<DoctorSlot> slots;
        vector<PatientVisit> visits;

        string query = "SELECT p.patient_id, p.first_name, p.last_name, p.middle_name, p.birth_date, p.contact, ws.work_date, ws.start_time, d.last_name + ' ' + d.first_name + ' ' + d.middle_name AS doctor_name, COALESCE(diag.diagnosis, '') AS diagnosis, COALESCE(diag.treatment, '') AS treatment FROM Patients p JOIN Appointments a ON p.patient_id = a.patient_id JOIN WorkSlots ws ON a.slot_id = ws.slot_id JOIN Doctors d ON ws.doctor_id = d.doctor_id LEFT JOIN Diagnosis diag ON a.appointment_id = diag.appointment_id WHERE p.first_name = ? AND p.last_name = ? AND p.middle_name = ? AND p.birth_date = ? AND p.contact = ? AND a.is_completed = 0 ORDER BY ws.work_date DESC, ws.start_time DESC;";

        auto results = dbManager.executeSQLWithResults(query, {firstName, lastName, middleName, birthDate, contact}, 12);
        
        for (auto& row : results) {
            visits.emplace_back(stoi(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]);
        }

        return visits;
    }
    
    bool cancelAppointment(DatabaseManager &dbManager, const string &firstName, const string &lastName, const string &middleName,const string &birthDate, const string &contact, const string &visitDate, const string &visitTime) {
        string query = "DELETE a FROM Appointments a JOIN Patients p ON a.patient_id = p.patient_id JOIN WorkSlots ws ON a.slot_id = ws.slot_id WHERE p.first_name = ? AND p.last_name = ? AND p.middle_name = ? AND p.birth_date = ? AND p.contact = ? AND ws.work_date = ? AND ws.start_time = ?";

        return dbManager.executeSQL(query, {firstName, lastName, middleName, birthDate, contact, visitDate, visitTime});
    }

};

class Doctor : public Person {
private:
    string specialization;
    string login;
    string password;
    string contact;
public:
    Doctor(int id, const string &firstName, const string &lastName, const string &middleName, const string &specialization, const string &login, const string &password, const string &contact) : Person(id, firstName, lastName, middleName), specialization(specialization), login(login),password(password), contact(contact) {}

    int getId() const {
        return id;
    }
    
    string getRole() const override {
        return "DOCTOR";
    }
    
    string toString() const {
        stringstream ss;
        ss << id << "|" << firstName << "|" << lastName << "|" << middleName << "|" << specialization << "|" << contact;
        return ss.str();
    }
    
    vector<PatientVisit> getDoctorAppointmentsForToday(DatabaseManager &dbManager, int doctorId, const string &todayDate) {
        vector<PatientVisit> visits;

        string query = "SELECT p.patient_id, p.first_name, p.last_name, p.middle_name, p.birth_date, p.contact, ws.work_date, ws.start_time, CONCAT(d.last_name, ' ', d.first_name, ' ', d.middle_name) AS doctor_name FROM Appointments a JOIN WorkSlots ws ON a.slot_id = ws.slot_id JOIN Patients p ON a.patient_id = p.patient_id JOIN Doctors d ON ws.doctor_id = d.doctor_id WHERE ws.work_date = ? AND ws.doctor_id = ? AND a.is_completed = 0 ORDER BY ws.start_time";

        auto results = dbManager.executeSQLWithResults(query, {todayDate, to_string(doctorId)}, 9);

        for (const auto& row : results) {
            visits.emplace_back(stoi(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], "", "");
        }

        return visits;
    }

    bool addDiagnosisAndCompleteAppointment(DatabaseManager &dbManager, const string &last_name, const string &first_name, const string &middle_name, const string &visit_date, const string &visit_time, const string &doctor_id, const string &diagnosis, const string &treatment) {
        string appointment_id;

        try {
            dbManager.executeSQL("BEGIN TRANSACTION;", {});

            string getAppointmentQuery = "SELECT a.appointment_id FROM Appointments a JOIN Patients p ON a.patient_id = p.patient_id JOIN WorkSlots ws ON a.slot_id = ws.slot_id WHERE p.last_name = ? AND p.first_name = ? AND p.middle_name = ? AND ws.work_date = ? AND ws.start_time = ? AND ws.doctor_id = ?;";
            auto result = dbManager.executeSQLWithResults(getAppointmentQuery, {last_name, first_name, middle_name, visit_date, visit_time, doctor_id}, 1);

            if (result.empty()) {
                dbManager.executeSQL("ROLLBACK;", {});
                return false;
            }

            appointment_id = result[0][0];

            string insertDiagnosisQuery = "INSERT INTO Diagnosis (appointment_id, diagnosis, treatment) VALUES (?, ?, ?)";
            if (!dbManager.executeSQL(insertDiagnosisQuery, {appointment_id, diagnosis, treatment})) {
                dbManager.executeSQL("ROLLBACK;", {});
                return false;
            }

            string updateAppointmentQuery = "UPDATE Appointments SET is_completed = 1 WHERE appointment_id = ?";
            if (!dbManager.executeSQL(updateAppointmentQuery, {appointment_id})) {
                dbManager.executeSQL("ROLLBACK;", {});
                return false;
            }

            dbManager.executeSQL("COMMIT;", {});
            return true;

        } catch (const exception &e) {
            dbManager.executeSQL("ROLLBACK;", {});
            cerr << "Transaction failed: " << e.what() << endl;
            return false;
        }
    }
};

class ServerManager {
private:
    int serverSocket;
    struct sockaddr_in serverAddress;
    DatabaseManager& dbManager;
public:
    ServerManager(DatabaseManager& db) : dbManager(db) {
        serverSocket = socket(AF_INET, SOCK_STREAM, 0);
        serverAddress.sin_family = AF_INET;
        serverAddress.sin_addr.s_addr = INADDR_ANY;
        serverAddress.sin_port = htons(LOGIN_PORT);
    }

    ~ServerManager() {
        close(serverSocket);
    }
    
    void sendResponse(int clientSocket, const string& message) {
        send(clientSocket, message.c_str(), message.size(), 0);
    }
    
    Person* verifyUserHelper(const string &query, const vector<string> &params, bool isAdmin) {
        SQLHSTMT stmt = dbManager.prepareStatement(query, params);
        if (!stmt) return nullptr;

        if (SQLFetch(stmt) == SQL_SUCCESS) {
            SQLINTEGER id;
            SQLCHAR firstName[50], lastName[50], middleName[50], specialization[100], contact[20];

            SQLGetData(stmt, 1, SQL_C_LONG, &id, 0, nullptr);
            SQLGetData(stmt, 2, SQL_C_CHAR, firstName, sizeof(firstName), nullptr);
            SQLGetData(stmt, 3, SQL_C_CHAR, lastName, sizeof(lastName), nullptr);
            SQLGetData(stmt, 4, SQL_C_CHAR, middleName, sizeof(middleName), nullptr);

            if (!isAdmin) {
                SQLGetData(stmt, 5, SQL_C_CHAR, specialization, sizeof(specialization), nullptr);
                SQLGetData(stmt, 6, SQL_C_CHAR, contact, sizeof(contact), nullptr);
            }
            
            SQLFreeHandle(SQL_HANDLE_STMT, stmt);
            
            if (isAdmin) {
                return new Admin(id, (char*)firstName, (char*)lastName, (char*)middleName, params[0], params[1]);
            } else {
                return new Doctor(id, (char*)firstName, (char*)lastName, (char*)middleName, (char*)specialization, params[0], params[1], (char*)contact);
            }
        }
        SQLFreeHandle(SQL_HANDLE_STMT, stmt);
        return nullptr;
    }

    Person* verifyUser(const string &username, const string &password) {
        string queryAdmins = "SELECT admin_id, first_name, last_name, middle_name FROM Admins WHERE login = ? AND password = ?";
        string queryDoctors = "SELECT doctor_id, first_name, last_name, middle_name, specialization, contact FROM Doctors WHERE login = ? AND password = ?";
        
        Person* user = verifyUserHelper(queryAdmins, {username, password}, true);
        if (!user) user = verifyUserHelper(queryDoctors, {username, password}, false);
        return user;
    }

    void start() {
        bind(serverSocket, (struct sockaddr*)&serverAddress, sizeof(serverAddress));
        listen(serverSocket, 3);
        cout << "Сервер запущено. Очікування підключень для авторизації...\n";

        while (true) {
            struct sockaddr_in clientAddress;
            socklen_t clientAddressLen = sizeof(clientAddress);
            int clientSocket = accept(serverSocket, (struct sockaddr*)&clientAddress, &clientAddressLen);

            char buffer[BUFFER_SIZE];
            memset(buffer, 0, BUFFER_SIZE);
            read(clientSocket, buffer, BUFFER_SIZE);

            stringstream ss(buffer);
            string command, username, password;
            
            getline(ss, command, ',');
            getline(ss, username, ',');
            getline(ss, password, ',');
            
            if (command == "LOGIN") {
                Person* user = verifyUser(username, password);

                if (user) {
                    if (user->getRole() == "ADMIN") {
                        sendResponse(clientSocket, user->getRole());
                        handleAdminRequests(user);
                    } else if (user->getRole() == "DOCTOR") {
                        Doctor *doctor = dynamic_cast<Doctor*>(user);
                        
                        if (doctor) {
                            string response = "DOCTOR;" + doctor->toString();
                            sendResponse(clientSocket, response);
                        }
                        
                        handleDoctorRequests(user);
                    }
                    
                    delete user;
                } else {
                    sendResponse(clientSocket, "INVALID_CREDENTIALS");
                }
            } else {
                sendResponse(clientSocket, "DB_ERROR");
            }
            close(clientSocket);
        }
    }

    void handleAdminRequests(Person *user) {
        Admin *admin = dynamic_cast<Admin*>(user);
        struct sockaddr_in clientAddress;
        socklen_t clientAddressLen = sizeof(clientAddress);
        char buffer[BUFFER_SIZE];

        cout << "Адміністратор авторизований. Очікування нових запитів...\n";
        while (true) {
            int adminSocket = accept(serverSocket, (struct sockaddr*)&clientAddress, &clientAddressLen);
            memset(buffer, 0, BUFFER_SIZE);
            read(adminSocket, buffer, BUFFER_SIZE);

            stringstream ss(buffer);
            string command;

            getline(ss, command, ',');

            try {
                if (command == "ADD_PATIENT") {
                    try {
                        string firstName, lastName, middleName, birthDate, contact;
                        
                        getline(ss, firstName, ',');
                        getline(ss, lastName, ',');
                        getline(ss, middleName, ',');
                        getline(ss, birthDate, ',');
                        getline(ss, contact, ',');
                        
                        Patient patient = admin->addPatient(dbManager, firstName, lastName, middleName, birthDate, contact);
                        string data = "SUCCESS;" + patient.toString();
                        sendResponse(adminSocket, data);
                    } catch (const runtime_error &e) {
                        sendResponse(adminSocket, e.what());
                    }
                } else if (command == "DELETE_PATIENT") {
                    string firstName, lastName, middleName, birthDate, contact;
                    
                    getline(ss, firstName, ',');
                    getline(ss, lastName, ',');
                    getline(ss, middleName, ',');
                    getline(ss, birthDate, ',');
                    getline(ss, contact, ',');
                    
                    if (admin->deletePatient(dbManager, firstName, lastName, middleName, birthDate, contact)) {
                        sendResponse(adminSocket, "SUCCESS");
                    } else {
                        sendResponse(adminSocket, "NOT_FOUND");
                    }
                } else if (command == "SEARCH_PATIENT") {
                    try {
                        string firstName, lastName, middleName, birthDate, contact;
                        
                        getline(ss, firstName, ',');
                        getline(ss, lastName, ',');
                        getline(ss, middleName, ',');
                        getline(ss, birthDate, ',');
                        getline(ss, contact, ',');
                        
                        Patient patient = admin->searchPatient(dbManager, firstName, lastName, middleName, birthDate, contact);
                        string data = "SUCCESS;" + patient.toString();
                        sendResponse(adminSocket, data);
                    } catch (const runtime_error &e) {
                        sendResponse(adminSocket, e.what());
                    }
                } else if (command == "GET_PATIENTS") {
                    vector<Patient> patients = admin->getAllPatients(dbManager);
                    if (!patients.empty()) {
                        stringstream dataStream;
                        for (const auto &patient : patients) {
                            dataStream << patient.toString() << "\n";
                        }

                        string data = "SUCCESS;" + dataStream.str();
                        sendResponse(adminSocket, data);
                    } else {
                        sendResponse(adminSocket, "NO_PATIENTS");
                    }
                } else if (command == "GET_PATIENT_VISITS") {
                    try {
                        string id;
                        
                        getline(ss, id, ',');
                        
                        vector<PatientVisit> visits = admin->getPatientVisits(dbManager, stoi(id));
                        if (!visits.empty()) {
                            stringstream dataStream;

                            for (const auto &visit : visits) {
                                dataStream << visit.toString() << "\n";
                            }

                            string data = "SUCCESS;" + dataStream.str();
                            sendResponse(adminSocket, data);
                        } else {
                            sendResponse(adminSocket, "NO_VISITS");
                        }
                    } catch (const exception &e) {
                        sendResponse(adminSocket, "ERROR");
                    }
                } else if (command == "CHECK_PATIENT_DOCTOR") {
                    try {
                        string patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact;
                        string doctor_first_name, doctor_last_name, doctor_middle_name;
                        
                        getline(ss, patient_first_name, ',');
                        getline(ss, patient_last_name, ',');
                        getline(ss, patient_middle_name, ',');
                        getline(ss, patient_birth_date, ',');
                        getline(ss, patient_contact, ',');
                        getline(ss, doctor_first_name, ',');
                        getline(ss, doctor_last_name, ',');
                        getline(ss, doctor_middle_name, ',');
                        
                        bool patientExists = admin->isPatientExists(dbManager, patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact);

                        bool doctorExists = admin->isDoctorExists(dbManager, doctor_first_name, doctor_last_name, doctor_middle_name);
                        
                        if (patientExists && doctorExists) {
                            string data = "SUCCESS";
                            sendResponse(adminSocket, data);
                        } else if (!patientExists && doctorExists) {
                            sendResponse(adminSocket, "NOT_FOUND_Patient");
                        } else if (patientExists && !doctorExists) {
                            sendResponse(adminSocket, "NOT_FOUND_Doctor");
                        } else {
                            sendResponse(adminSocket, "NOT_FOUND_Patient_AND_Doctor");
                        }
                    } catch (const exception &e) {
                        sendResponse(adminSocket, "ERROR");
                    }
                } else if (command == "GET_AVAILABLE_SLOTS") {
                    try {
                        
                        string doctor_first_name, doctor_last_name, doctor_middle_name, date;
                        
                        getline(ss, doctor_first_name, ',');
                        getline(ss, doctor_last_name, ',');
                        getline(ss, doctor_middle_name, ',');
                        getline(ss, date, ',');
                        
                        vector<DoctorSlot> slots = admin->getAvailableDoctorSlotsForDay(dbManager, doctor_first_name, doctor_last_name, doctor_middle_name, date);

                        if (!slots.empty()) {
                            stringstream dataStream;
                                
                            for (const auto &slot : slots) {
                                dataStream << slot.toString() << "\n";
                            }
                                
                            string data = "SUCCESS;" + dataStream.str();
                            sendResponse(adminSocket, data);
                        } else {
                            sendResponse(adminSocket, "NO_SLOTS");
                        }
                    } catch (const exception &e) {
                        sendResponse(adminSocket, "ERROR");
                    }
                } else if (command == "BOOK_APPOINTMENT") {
                    try {
                        string slot_id, patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact;

                        getline(ss, slot_id, ',');
                        getline(ss, patient_first_name, ',');
                        getline(ss, patient_last_name, ',');
                        getline(ss, patient_middle_name, ',');
                        getline(ss, patient_birth_date, ',');
                        getline(ss, patient_contact, ',');

                        // Виклик функції для створення запису
                        bool result = admin->bookAppointment(dbManager, stoi(slot_id), patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact);

                        if (result) {
                            sendResponse(adminSocket, "SUCCESS");
                        } else {
                            sendResponse(adminSocket, "ALREADY_BOOKED");
                        }
                    } catch (const exception &e) {
                        sendResponse(adminSocket, "ERROR");
                    }
                } else if (command == "GET_PATIENT_APPOINTMENT") {
                    try {
                        string patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact;

                        getline(ss, patient_first_name, ',');
                        getline(ss, patient_last_name, ',');
                        getline(ss, patient_middle_name, ',');
                        getline(ss, patient_birth_date, ',');
                        getline(ss, patient_contact, ',');

                        bool patientExists = admin->isPatientExists(dbManager, patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact);

                        if (!patientExists) {
                            sendResponse(adminSocket, "NOT_FOUND_Patient");
                        }

                        vector<PatientVisit> visits = admin->getPatientAppointments(dbManager, patient_first_name, patient_last_name, patient_middle_name, patient_birth_date, patient_contact);

                        if (!visits.empty()) {
                            stringstream dataStream;

                            for (const auto &visit : visits) {
                                dataStream << visit.toString() << "\n";
                            }

                            string data = "SUCCESS;" + dataStream.str();
                            sendResponse(adminSocket, data);
                        } else {
                            sendResponse(adminSocket, "NO_APPOINTMENTS");
                        }

                    } catch (const exception &e) {
                        sendResponse(adminSocket, "ERROR");
                    }
                } else if (command == "CANCEL_APPOINTMENT") {
                    try {
                        string first_name, last_name, middle_name, birth_date, contact, visit_date, visit_time;
                        
                        getline(ss, first_name, ',');
                        getline(ss, last_name, ',');
                        getline(ss, middle_name, ',');
                        getline(ss, birth_date, ',');
                        getline(ss, contact, ',');
                        getline(ss, visit_date, ',');
                        getline(ss, visit_time, ',');

                        bool success = admin->cancelAppointment(dbManager, first_name, last_name, middle_name, birth_date, contact, visit_date, visit_time);

                        if (success) {
                            sendResponse(adminSocket, "SUCCESS");
                        } else {
                            sendResponse(adminSocket, "NOT_FOUND");
                        }
                    } catch (const exception &e) {
                        sendResponse(adminSocket, "ERROR");
                    }
                } else if (command == "LOGOUT") {
                    cout << "Адміністратор вийшов із системи\n";
                    close(adminSocket);
                    break;
                }
            } catch (const runtime_error& e) {
                sendResponse(adminSocket, e.what());
            }
            close(adminSocket);
        }
    }
    
    void handleDoctorRequests(Person *user) {
        Doctor* doctor = dynamic_cast<Doctor*>(user);
        struct sockaddr_in clientAddress;
        socklen_t clientAddressLen = sizeof(clientAddress);
        char buffer[BUFFER_SIZE];

        cout << "Лікар авторизований. Очікування нових запитів...\n";
        while (true) {
            int doctorSocket = accept(serverSocket, (struct sockaddr*)&clientAddress, &clientAddressLen);
            memset(buffer, 0, BUFFER_SIZE);
            read(doctorSocket, buffer, BUFFER_SIZE);

            stringstream ss(buffer);
            string command;

            getline(ss, command, '|');

            try {
                if (command == "GET_TODAY_APPOINTMENTS") {
                    try {
                        string today_date;
                        
                        getline(ss, today_date, '|');

                        vector<PatientVisit> visits = doctor->getDoctorAppointmentsForToday(dbManager, doctor->getId(), today_date);

                        if (!visits.empty()) {
                            stringstream dataStream;
                            
                            for (const auto &visit : visits) {
                                dataStream << visit.toString() << "\n";
                            }

                            string data = "SUCCESS;" + dataStream.str();
                            sendResponse(doctorSocket, data);
                        } else {
                            sendResponse(doctorSocket, "NO_APPOINTMENTS");
                        }
                    } catch (const exception &e) {
                        sendResponse(doctorSocket, "ERROR");
                    }
                } else if (command == "ADD_DIAGNOSIS") {
                    try {
                        string last_name, first_name, middle_name, visit_date, visit_time, diagnosis, treatment, doctor_id;

                        getline(ss, last_name, '|');
                        getline(ss, first_name, '|');
                        getline(ss, middle_name, '|');
                        getline(ss, visit_date, '|');
                        getline(ss, visit_time, '|');
                        getline(ss, diagnosis, '|');
                        getline(ss, treatment, '|');
                        getline(ss, doctor_id, '|');
                        
                        if (doctor->addDiagnosisAndCompleteAppointment(dbManager, last_name, first_name, middle_name, visit_date, visit_time, doctor_id, diagnosis, treatment)) {
                            sendResponse(doctorSocket, "SUCCESS");
                        } else {
                            sendResponse(doctorSocket, "NOT_FOUND");
                        }
                    } catch (const exception &e) {
                        sendResponse(doctorSocket, "ERROR");
                    }
                } else if (command == "LOGOUT") {
                    cout << "Лікар вийшов із системи\n";
                    close(doctorSocket);
                    break;
                }
            } catch (const runtime_error& e) {
                sendResponse(doctorSocket, e.what());
            }
            close(doctorSocket);
        }
    }

};

int main() {
    DatabaseManager dbManager;

    if (!dbManager.connect("SQLServer", "sa", "20060416My")) {
        cerr << "Помилка підключення до БД." << endl;
        return -1;
    }

    ServerManager server(dbManager);
    server.start();

    return 0;
}
