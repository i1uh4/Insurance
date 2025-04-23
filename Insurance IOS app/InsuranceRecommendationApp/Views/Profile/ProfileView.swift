import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @State private var isEditing = false
    
    @State private var firstName = ""
    @State private var lastName = ""
    @State private var age = ""
    @State private var gender = "None"
    @State private var occupation = ""
    @State private var income = ""
    @State private var maritalStatus = "None"
    @State private var hasChildren = false
    @State private var hasVehicle = false
    @State private var hasHome = false
    @State private var hasMedicalConditions = false
    @State private var travelFrequency = "None"
    
    @State private var isRefreshing = false
    
    let genderOptions = ["None", "Male", "Female"]
    let maritalStatusOptions = ["None", "Single", "Married", "Divorced", "Widowed"]
    let travelFrequencyOptions = ["None", "Rarely", "Occasionally", "Frequently"]
    
    var body: some View {
        NavigationView {
            ZStack {
                Form {
                    Section(header: Text("Account Information")) {
                        LabeledContent("Username", value: authViewModel.user?.name ?? "")
                        LabeledContent("Email", value: authViewModel.user?.email ?? "")
                    }
                    
                    Section(header: Text("Personal Information")) {
                        if isEditing {
                            TextField("First Name", text: $firstName)
                            TextField("Last Name", text: $lastName)
                            TextField("Age", text: $age)
                                .keyboardType(.numberPad)
                            
                            Picker("Gender", selection: $gender) {
                                ForEach(genderOptions, id: \.self) {
                                    Text($0)
                                }
                            }
                            
                            TextField("Occupation", text: $occupation)
                            TextField("Annual Income", text: $income)
                                .keyboardType(.decimalPad)
                            
                            Picker("Marital Status", selection: $maritalStatus) {
                                ForEach(maritalStatusOptions, id: \.self) {
                                    Text($0)
                                }
                            }
                        } else {
                            LabeledContent("First Name", value: authViewModel.user?.firstName ?? "Not set")
                            LabeledContent("Last Name", value: authViewModel.user?.lastName ?? "Not set")
                            LabeledContent("Age", value: authViewModel.user?.age != nil ? "\(authViewModel.user!.age!)" : "Not set")
                            LabeledContent("Gender", value: authViewModel.user?.gender ?? "Not set")
                            LabeledContent("Occupation", value: authViewModel.user?.occupation ?? "Not set")
                            LabeledContent("Annual Income", value: authViewModel.user?.income != nil ? "$\(Int(authViewModel.user!.income!))" : "Not set")
                            LabeledContent("Marital Status", value: authViewModel.user?.maritalStatus ?? "Not set")
                        }
                    }
                    
                    Section(header: Text("Additional Information")) {
                        if isEditing {
                            Toggle("Have Children", isOn: $hasChildren)
                            Toggle("Own a Vehicle", isOn: $hasVehicle)
                            Toggle("Own a Home", isOn: $hasHome)
                            Toggle("Have Medical Conditions", isOn: $hasMedicalConditions)
                            
                            Picker("Travel Frequency", selection: $travelFrequency) {
                                ForEach(travelFrequencyOptions, id: \.self) {
                                    Text($0)
                                }
                            }
                        } else {
                            LabeledContent("Have Children", value: (authViewModel.user?.hasChildren ?? false) ? "Yes" : "No")
                            LabeledContent("Own a Vehicle", value: (authViewModel.user?.hasVehicle ?? false) ? "Yes" : "No")
                            LabeledContent("Own a Home", value: (authViewModel.user?.hasHome ?? false) ? "Yes" : "No")
                            LabeledContent("Have Medical Conditions", value: (authViewModel.user?.hasMedicalConditions ?? false) ? "Yes" : "No")
                            LabeledContent("Travel Frequency", value: authViewModel.user?.travelFrequency ?? "Not set")
                        }
                    }
                    
                    Section {
                        if isEditing {
                            Button("Save Changes") {
                                saveChanges()
                            }
                            .foregroundColor(.blue)
                            
                            Button("Cancel") {
                                isEditing = false
                                loadUserData()
                            }
                            .foregroundColor(.red)
                        } else {
                            Button("Edit Profile") {
                                loadUserData()
                                isEditing = true
                            }
                            .foregroundColor(.blue)
                        }
                        
                        Button("Logout") {
                            authViewModel.logout()
                        }
                        .foregroundColor(.red)
                    }
                }
                .navigationTitle("Profile")
                .onAppear {
                    fetchUserProfile()
                }
                .refreshable {
                    await refreshUserProfile()
                }
                
                if authViewModel.isLoading || isRefreshing {
                    LoadingView(message: isRefreshing ? "Refreshing profile..." : "Saving profile...")
                }
            }
            .alert(item: $authViewModel.profileAlert) { alert in
                Alert(
                    title: Text(alert.title),
                    message: Text(alert.message),
                    dismissButton: .default(Text(alert.dismissButton)) {
                        if let action = alert.action {
                            action()
                        }
                    }
                )
            }
        }
    }
    
    private func loadUserData() {
        guard let user = authViewModel.user else { return }
        
        firstName = user.firstName ?? ""
        lastName = user.lastName ?? ""
        age = user.age != nil ? "\(user.age!)" : ""
        gender = user.gender ?? "Male"
        occupation = user.occupation ?? ""
        income = user.income != nil ? "\(user.income!)" : ""
        maritalStatus = user.maritalStatus ?? "Single"
        hasChildren = user.hasChildren ?? false
        hasVehicle = user.hasVehicle ?? false
        hasHome = user.hasHome ?? false
        hasMedicalConditions = user.hasMedicalConditions ?? false
        travelFrequency = user.travelFrequency ?? "Rarely"
    }
    
    private func fetchUserProfile() {
        guard let email = authViewModel.user?.email else { return }
        
        isRefreshing = true
        
        Task {
            do {
                let updatedUser = try await AuthService.shared.fetchUserProfile(email: email)
                
                await MainActor.run {
                    authViewModel.user = updatedUser
                    loadUserData()
                    isRefreshing = false
                }
            } catch {
                await MainActor.run {
                    authViewModel.profileAlert = AlertItem(
                        title: "Error",
                        message: "Failed to fetch profile: \(error.localizedDescription)",
                        dismissButton: "OK"
                    )
                    isRefreshing = false
                }
            }
        }
    }
    
    private func refreshUserProfile() async {
        guard let email = authViewModel.user?.email else { return }
        
        do {
            let updatedUser = try await AuthService.shared.fetchUserProfile(email: email)
            
            await MainActor.run {
                authViewModel.user = updatedUser
                loadUserData()
            }
        } catch {
            await MainActor.run {
                authViewModel.profileAlert = AlertItem(
                    title: "Error",
                    message: "Failed to refresh profile: \(error.localizedDescription)",
                    dismissButton: "OK"
                )
            }
        }
    }
    
    private func saveChanges() {
        guard let currentUser = authViewModel.user else { return }
        var updatedFields: [String: Any] = [:]
        
        if firstName != (currentUser.firstName ?? "") {
            updatedFields["first_name"] = firstName.isEmpty ? nil : firstName
        }
        
        if lastName != (currentUser.lastName ?? "") {
            updatedFields["last_name"] = lastName.isEmpty ? nil : lastName
        }
        
        let currentAge = currentUser.age != nil ? "\(currentUser.age!)" : ""
        if age != currentAge && !age.isEmpty {
            updatedFields["age"] = Int(age)
        }
        
        if gender != (currentUser.gender ?? "Male") {
            updatedFields["gender"] = gender
        }
        
        if occupation != (currentUser.occupation ?? "") {
            updatedFields["occupation"] = occupation.isEmpty ? nil : occupation
        }
        
        let currentIncome = currentUser.income != nil ? "\(currentUser.income!)" : ""
        if income != currentIncome && !income.isEmpty {
            updatedFields["income"] = Double(income)
        }
        
        if maritalStatus != (currentUser.maritalStatus ?? "Single") {
            updatedFields["marital_status"] = maritalStatus
        }
        
        if hasChildren != (currentUser.hasChildren ?? false) {
            updatedFields["has_children"] = hasChildren
        }
        
        if hasVehicle != (currentUser.hasVehicle ?? false) {
            updatedFields["has_vehicle"] = hasVehicle
        }
        
        if hasHome != (currentUser.hasHome ?? false) {
            updatedFields["has_home"] = hasHome
        }
        
        if hasMedicalConditions != (currentUser.hasMedicalConditions ?? false) {
            updatedFields["has_medical_conditions"] = hasMedicalConditions
        }
        
        if travelFrequency != (currentUser.travelFrequency ?? "Rarely") {
            updatedFields["travel_frequency"] = travelFrequency
        }
        
        if !updatedFields.isEmpty {
            authViewModel.updateProfile(updatedFields: updatedFields)
        }
        
        isEditing = false
        
        fetchUserProfile()
    }
}
