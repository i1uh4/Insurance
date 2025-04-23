import Foundation

class RecommendationViewModel: ObservableObject {
    @Published var recommendations: [InsuranceProduct] = []
    @Published var isLoading = false
    @Published var recommendationAlert: AlertItem?
    
    func getRecommendations(for user: User) {
        guard user.isProfileComplete else {
            self.recommendationAlert = AlertItem(
                title: "Incomplete Profile",
                message: "Please complete your profile to get personalized recommendations."
            )
            return
        }
        
        let request = InsuranceRecommendationRequest(
            age: user.age!,
            gender: user.gender!,
            occupation: user.occupation!,
            income: user.income!,
            maritalStatus: user.maritalStatus!,
            hasChildren: user.hasChildren!,
            hasVehicle: user.hasVehicle!,
            hasHome: user.hasHome!,
            hasMedicalConditions: user.hasMedicalConditions!,
            travelFrequency: user.travelFrequency!
        )
        
        isLoading = true
        recommendationAlert = nil
        
        Task {
            do {
                let recommendations = try await AuthService.shared.getRecommendations(request: request)
                DispatchQueue.main.async {
                    self.recommendations = recommendations
                    self.isLoading = false
                    
                    if recommendations.isEmpty {
                        self.recommendationAlert = AlertItem(
                            title: "No Recommendations",
                            message: "We couldn't find any insurance recommendations based on your profile. Try adjusting your profile information."
                        )
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    self.recommendationAlert = self.createAlert(from: error)
                    self.isLoading = false
                }
            }
        }
    }
    
    private func createAlert(from error: Error) -> AlertItem {
        if let apiError = error as? APIError {
            switch apiError {
            case .unauthorized:
                return AlertItem(
                    title: "Authentication Error",
                    message: "Your session has expired. Please log in again."
                )
            case .validationError(let message):
                return AlertItem(
                    title: "Validation Error",
                    message: message
                )
            case .serverError(let message):
                return AlertItem(
                    title: "Server Error",
                    message: "There was a problem with the server: \(message)"
                )
            case .invalidURL:
                return AlertItem(
                    title: "Connection Error",
                    message: "Invalid URL. Please check your connection."
                )
            case .requestFailed(let error):
                return AlertItem(
                    title: "Request Failed",
                    message: "There was a problem with your request: \(error.localizedDescription)"
                )
            case .invalidResponse:
                return AlertItem(
                    title: "Server Error",
                    message: "Received an invalid response from the server."
                )
            case .decodingFailed(let error):
                return AlertItem(
                    title: "Data Error",
                    message: "Could not process the data from the server: \(error.localizedDescription)"
                )
            case .unknownError(let message):
                return AlertItem(
                    title: "Unknown Error",
                    message: message
                )
            default:
                return AlertItem(
                    title: "Error",
                    message: "An unexpected error occurred."
                )
            }
        }
        
        return AlertItem(
            title: "Error",
            message: error.localizedDescription
        )
    }
}
