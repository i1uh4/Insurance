import Foundation
import SwiftUI

class AuthViewModel: ObservableObject {
    @Published var user: User?
    @Published var isAuthenticated = false
    @Published var isLoading = false
    @Published var loginAlert: AlertItem?
    @Published var registerAlert: AlertItem?
    @Published var profileAlert: AlertItem?
    @Published var navigateToLogin = false
    
    func checkAuthStatus() {
        if UserDefaults.standard.string(forKey: "authToken") != nil {
            self.isAuthenticated = true
        }
    }
    
    func login(email: String, password: String) {
        isLoading = true
        loginAlert = nil
        
        Task {
            do {
                let user = try await AuthService.shared.login(email: email, password: password)
                DispatchQueue.main.async {
                    self.user = user
                    self.isAuthenticated = true
                    self.isLoading = false
                }
            } catch {
                DispatchQueue.main.async {
                    self.loginAlert = self.createAlert(from: error)
                    self.isLoading = false
                }
            }
        }
    }
    
    func register(user_name: String, email: String, password: String) {
        isLoading = true
        registerAlert = nil
        
        Task {
            do {
                let message = try await AuthService.shared.register(user_name: user_name, email: email, password: password)
                DispatchQueue.main.async {
                    self.isLoading = false
                    self.registerAlert = AlertItem(
                        title: "Success",
                        message: message,
                        dismissButton: "OK",
                        action: {
                            self.navigateToLogin = true
                        }
                    )
                }
            } catch {
                DispatchQueue.main.async {
                    self.registerAlert = self.createAlert(from: error)
                    self.isLoading = false
                }
            }
        }
    }
    
    func logout() {
        AuthService.shared.logout()
        self.user = nil
        self.isAuthenticated = false
    }
    
    func updateProfile(updatedFields: [String: Any]) {
        isLoading = true
        profileAlert = nil
        
        Task {
            do {
                let updatedUser = try await AuthService.shared.updateUserProfile(updatedFields: updatedFields)
                DispatchQueue.main.async {
                    self.user = updatedUser
                    self.isLoading = false
                    self.profileAlert = AlertItem(
                        title: "Success",
                        message: "Your profile has been updated successfully."
                    )
                }
            } catch {
                DispatchQueue.main.async {
                    self.profileAlert = self.createAlert(from: error)
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
                    title: "Authentication Failed",
                    message: "Invalid username or password. Please try again."
                )
            case .validationError(let message):
                return AlertItem(
                    title: "Validation Error",
                    message: message
                )
            case .clientError(let message):
                return AlertItem(
                    title: "Client Error",
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
            case .emptyFields:
                return AlertItem(
                    title: "Missing Information",
                    message: "All fields must be filled in."
                )
            case .invalidEmail:
                return AlertItem(
                    title: "Invalid Email",
                    message: "Please enter a valid email address."
                )
            }
        }
        
        return AlertItem(
            title: "Error",
            message: error.localizedDescription
        )
    }
}
