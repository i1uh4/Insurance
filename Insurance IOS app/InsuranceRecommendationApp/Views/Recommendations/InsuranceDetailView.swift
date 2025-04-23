import SwiftUI


struct InsuranceDetailView: View {
    var insurance: InsuranceProduct
    @State private var isPurchaseFormPresented = false
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                
                VStack(alignment: .leading, spacing: 12) {
                    Text(insurance.productName)
                        .font(.title)
                        .fontWeight(.bold)
                        
                    Text(insurance.provider)
                        .font(.headline)
                        .foregroundColor(.secondary)
                    
                    HStack(spacing: 10) {
                        Label("\(insurance.category)", systemImage: getCategoryIcon(for: insurance.category))
                            .font(.subheadline)
                        
                        Spacer()
                        
                        HStack {
                            Text("Score:")
                                .font(.subheadline)
                            
                            Text(String(format: "%.1f", insurance.matchScore * 10))
                                .font(.headline)
                                .foregroundColor(.blue)
                            
                            Text("/10")
                                .font(.subheadline)
                        }
                    }
                    .padding(.top, 4)
                }
                .padding(.bottom, 10)
                
                // Price section
                VStack(alignment: .leading, spacing: 8) {
                    Text("Estimated Price")
                        .font(.headline)
                    
                    HStack(alignment: .firstTextBaseline) {
                        Text("₽\(Int(insurance.estimatedPrice))")
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundColor(.blue)
                        
                        Text("per year")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .padding(.leading, 4)
                    }
                }
                .padding(.vertical, 16)
                .padding(.horizontal, 20)
                .background(Color(.systemGray6))
                .cornerRadius(12)
                
                // Description section
                VStack(alignment: .leading, spacing: 12) {
                    Text("Description")
                        .font(.headline)
                    
                    Text(insurance.description)
                        .font(.body)
                        .fixedSize(horizontal: false, vertical: true)
                }
                
                // Features section
                VStack(alignment: .leading, spacing: 12) {
                    Text("Features")
                        .font(.headline)
                    
                    ForEach(insurance.features, id: \.self) { feature in
                        Label(feature, systemImage: "checkmark.circle.fill")
                            .foregroundColor(.primary)
                            .font(.subheadline)
                    }
                }
                
                // Suitable for section
                if !insurance.suitableFor.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Suitable For")
                            .font(.headline)
                        
                        ForEach(insurance.suitableFor, id: \.self) { suitableFor in
                            Label(suitableFor, systemImage: "person.fill")
                                .foregroundColor(.primary)
                                .font(.subheadline)
                        }
                    }
                }
                
                // Risks covered section
                if !insurance.risksCovered.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Risks Covered")
                            .font(.headline)
                        
                        ForEach(insurance.risksCovered, id: \.self) { risk in
                            Label(risk, systemImage: "shield.fill")
                                .foregroundColor(.primary)
                                .font(.subheadline)
                        }
                    }
                }
                
                // Recommendation reason
                VStack(alignment: .leading, spacing: 12) {
                    Text("Why We Recommend This")
                        .font(.headline)
                    
                    Text(insurance.recommendationReason)
                        .font(.body)
                        .fixedSize(horizontal: false, vertical: true)
                }
                
                // Purchase button
                Button(action: {
                    isPurchaseFormPresented = true
                }) {
                    Text("Purchase Insurance")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(12)
                }
                .padding(.top, 10)
            }
            .padding()
        }
        .navigationTitle("Insurance Details")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $isPurchaseFormPresented) {
            PurchaseFormView(insurance: insurance)
        }
    }
    
    private func getCategoryIcon(for category: String) -> String {
        let category = insuranceCategories.first { $0.name == category }
        return category?.icon ?? "questionmark"
    }
}


struct PurchaseFormView: View {
    var insurance: InsuranceProduct
    @State private var name = ""
    @State private var email = ""
    @State private var phone = ""
    @State private var agreedToTerms = false
    @Environment(\.presentationMode) var presentationMode
    @State private var showingAlert = false
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Insurance Details")) {
                    HStack {
                        Text("Product")
                        Spacer()
                        Text(insurance.productName)
                            .foregroundColor(.secondary)
                    }
                    
                    HStack {
                        Text("Provider")
                        Spacer()
                        Text(insurance.provider)
                            .foregroundColor(.secondary)
                    }
                    
                    HStack {
                        Text("Price")
                        Spacer()
                        Text("₽\(Int(insurance.estimatedPrice)) / year")
                            .foregroundColor(.secondary)
                    }
                }
                
                Section(header: Text("Personal Information")) {
                    TextField("Full Name", text: $name)
                    TextField("Email", text: $email)
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                    TextField("Phone", text: $phone)
                        .keyboardType(.phonePad)
                }
                
                Section {
                    Toggle(isOn: $agreedToTerms) {
                        Text("I agree to the terms and conditions")
                    }
                }
                
                Section {
                    Button(action: {
                        // Here you would typically process the purchase
                        showingAlert = true
                    }) {
                        Text("Submit Application")
                            .frame(maxWidth: .infinity)
                            .multilineTextAlignment(.center)
                    }
                    .disabled(!isFormValid)
                }
            }
            .navigationTitle("Purchase Insurance")
            .navigationBarItems(trailing: Button("Cancel") {
                presentationMode.wrappedValue.dismiss()
            })
            .alert(isPresented: $showingAlert) {
                Alert(
                    title: Text("Application Submitted"),
                    message: Text("Thank you for your application! A representative will contact you shortly."),
                    dismissButton: .default(Text("OK")) {
                        presentationMode.wrappedValue.dismiss()
                    }
                )
            }
        }
    }
    
    var isFormValid: Bool {
        !name.isEmpty && !email.isEmpty && !phone.isEmpty && agreedToTerms
    }
}
