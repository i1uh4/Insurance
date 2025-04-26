import SwiftUI

struct RecommendationView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @StateObject var viewModel = RecommendationViewModel()
    @State private var selectedCategory: String? = nil
    @State private var showRefreshButton = true
    
    var filteredRecommendations: [InsuranceProduct] {
        if let category = selectedCategory {
            return viewModel.recommendations.filter { $0.category == category }
        }
        return viewModel.recommendations
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                VStack {
                    if viewModel.isLoading {
                        ProgressView("Getting your recommendations...")
                            .padding()
                    } else if viewModel.recommendations.isEmpty {
                        EmptyRecommendationsView(viewModel: viewModel, authViewModel: authViewModel)
                    } else {
                        RecommendationsContentView(
                            viewModel: viewModel,
                            selectedCategory: $selectedCategory,
                            filteredRecommendations: filteredRecommendations,
                            authViewModel: authViewModel
                        )
                    }
                }
                .navigationTitle("Recommendations")
                .toolbar {
                    if showRefreshButton {
                        ToolbarItem(placement: .navigationBarTrailing) {
                            Button(action: {
                                refreshRecommendations()
                            }) {
                                Label("Refresh", systemImage: "arrow.clockwise")
                            }
                        }
                    }
                }
                .onAppear {
                    if viewModel.recommendations.isEmpty {
                        if let user = authViewModel.user {
                            if user.isProfileComplete {
                                viewModel.getRecommendations(for: user)
                            }
                        }
                    }
                }
                
                if viewModel.isLoading {
                    LoadingView(message: "Getting recommendations...")
                }
            }
            .alert(item: $viewModel.recommendationAlert) { alert in
                Alert(
                    title: Text(alert.title),
                    message: Text(alert.message),
                    dismissButton: .default(Text(alert.dismissButton))
                )
            }
        }
    }
    
    private func refreshRecommendations() {
        if let user = authViewModel.user {
            viewModel.getRecommendations(for: user)
        }
    }
}

struct EmptyRecommendationsView: View {
    @ObservedObject var viewModel: RecommendationViewModel
    var authViewModel: AuthViewModel
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 70))
                .foregroundColor(.blue)
            
            Text("Get personalized insurance recommendations based on your profile")
                .font(.headline)
                .multilineTextAlignment(.center)
                .padding()
            
            CustomButton(
                title: "Get Recommendations",
                action: {
                    if let user = authViewModel.user {
                        viewModel.getRecommendations(for: user)
                    }
                }
            )
        }
        .padding()
    }
}

struct RecommendationsContentView: View {
    @ObservedObject var viewModel: RecommendationViewModel
    @Binding var selectedCategory: String?
    var filteredRecommendations: [InsuranceProduct]
    var authViewModel: AuthViewModel
    
    var body: some View {
        VStack {
            CategoryScrollView(
                selectedCategory: $selectedCategory,
                categories: getAvailableCategories()
            )
            .padding(.vertical, 10)
            
            if selectedCategory != nil {
                Text("Category: \(selectedCategory ?? "")")
                    .font(.headline)
                    .padding(.bottom, 5)
            }
            
            if filteredRecommendations.isEmpty {
                NoRecommendationsForCategoryView(resetAction: { selectedCategory = nil })
            } else {
                VStack {
                    HStack {
                        Text("Found \(filteredRecommendations.count) recommendations")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        
                        Spacer()
                        
                        Button(action: {
                            refreshRecommendations()
                        }) {
                            Label("Refresh", systemImage: "arrow.clockwise")
                                .font(.subheadline)
                        }
                    }
                    .padding(.horizontal)
                    
                    RecommendationsList(
                        recommendations: filteredRecommendations,
                        authViewModel: authViewModel
                    )
                }
            }
        }
    }
    
    private func getAvailableCategories() -> [InsuranceCategory] {
        let uniqueCategories = Set(viewModel.recommendations.map { $0.category })
        
        return insuranceCategories.filter { uniqueCategories.contains($0.name) }
    }
    
    private func refreshRecommendations() {
        if let user = authViewModel.user {
            viewModel.getRecommendations(for: user)
        }
    }
}

struct CategoryScrollView: View {
    @Binding var selectedCategory: String?
    var categories: [InsuranceCategory]
    
    var body: some View {
        VStack {
            Text("Insurance Categories")
                .font(.headline)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal)
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 15) {
                    CategoryButton(
                        title: "All",
                        isSelected: selectedCategory == nil,
                        action: { selectedCategory = nil }
                    )
                    
                    ForEach(categories) { category in
                        CategoryButton(
                            title: category.name,
                            icon: category.icon,
                            isSelected: selectedCategory == category.name,
                            action: { selectedCategory = category.name }
                        )
                    }
                }
                .padding(.horizontal)
            }
        }
    }
}

struct RecommendationsList: View {
    var recommendations: [InsuranceProduct]
    var authViewModel: AuthViewModel
    @StateObject private var insuranceViewModel = InsuranceViewModel()
    
    var body: some View {
        ScrollView {
            LazyVStack(spacing: 16) {
                ForEach(recommendations) { insurance in
                    NavigationLink(
                        destination: InsuranceDetailView(
                            insurance: insurance,
                            authViewModel: authViewModel,
                            insuranceViewModel: insuranceViewModel
                        )
                    ) {
                        InsuranceCard(insurance: insurance)
                    }
                    .buttonStyle(PlainButtonStyle())
                }
            }
            .padding()
        }
    }
}

struct NoRecommendationsForCategoryView: View {
    var resetAction: () -> Void
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "exclamationmark.circle")
                .font(.system(size: 50))
                .foregroundColor(.orange)
                .padding(.bottom, 10)
            
            Text("No recommendations found for this category")
                .font(.headline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding()
            
            Button(action: resetAction) {
                Text("Show All Recommendations")
                    .font(.headline)
                    .foregroundColor(.white)
                    .padding(.vertical, 10)
                    .padding(.horizontal, 20)
                    .background(Color.blue)
                    .cornerRadius(10)
            }
        }
        .padding()
    }
}

struct CategoryButton: View {
    var title: String
    var icon: String? = nil
    var isSelected: Bool
    var action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 5) {
                if let icon = icon {
                    Image(systemName: icon)
                        .font(.system(size: 14))
                }
                
                Text(title)
                    .font(.subheadline)
                    .fontWeight(isSelected ? .bold : .regular)
            }
            .padding(.vertical, 8)
            .padding(.horizontal, 16)
            .background(isSelected ? Color.blue : Color(.systemGray6))
            .foregroundColor(isSelected ? .white : .primary)
            .cornerRadius(20)
        }
    }
}

extension InsuranceProduct: Identifiable {
    var id: Int { productId }
}
