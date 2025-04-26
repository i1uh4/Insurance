import SwiftUI

struct InsuranceDetailView: View {
    var insurance: InsuranceProduct
    var authViewModel: AuthViewModel
    @ObservedObject var insuranceViewModel: InsuranceViewModel
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
                
                VStack(alignment: .leading, spacing: 12) {
                    Text("Why We Recommend This")
                        .font(.headline)
                    
                    Text(insurance.recommendationReason)
                        .font(.body)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
            .padding()
        }
        .navigationTitle("Insurance Details")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            if let user = authViewModel.user {
                insuranceViewModel.checkRecommendation(
                    productId: insurance.productId,
                    userEmail: user.email
                )
            }
        }
        .overlay(
            Group {
                if insuranceViewModel.isCheckingRecommendation {
                    ProgressView("Checking recommendation...")
                        .padding()
                        .background(Color(.systemBackground).opacity(0.8))
                        .cornerRadius(10)
                }
            }
        )
        .alert(isPresented: Binding<Bool>(
            get: { insuranceViewModel.checkRecommendationError != nil },
            set: { if !$0 { insuranceViewModel.checkRecommendationError = nil } }
        )) {
            Alert(
                title: Text("Error"),
                message: Text(insuranceViewModel.checkRecommendationError ?? "Unknown error"),
                dismissButton: .default(Text("OK"))
            )
        }
    }
    
    private func getCategoryIcon(for category: String) -> String {
        let category = insuranceCategories.first { $0.name == category }
        return category?.icon ?? "questionmark"
    }
}
