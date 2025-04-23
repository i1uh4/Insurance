import Foundation

class AuthService {
    static let shared = AuthService()

    private init() {}

    func login(email: String, password: String) async throws -> User {
        if email.isEmpty || password.isEmpty {
            throw APIError.emptyFields
        }

        let loginRequest = LoginRequest(email: email, password: password)
        let jsonData = try JSONEncoder().encode(loginRequest)

        let response: AuthResponse = try await APIService.shared.request(
            endpoint: "auth/login",
            method: "POST",
            body: jsonData,
            requiresAuth: false
        )

        UserDefaults.standard.set(response.accessToken, forKey: "authToken")
        return response.user
    }

    func register(name: String, email: String, password: String) async throws -> String {
        if name.isEmpty || email.isEmpty || password.isEmpty {
            throw APIError.emptyFields
        }

        if !Validators.isValidEmail(email) {
            throw APIError.invalidEmail
        }

        let registerRequest = RegisterRequest(name: name, email: email, password: password)
        let jsonData = try JSONEncoder().encode(registerRequest)

        let response: RegisterResponse = try await APIService.shared.request(
            endpoint: "auth/register",
            method: "POST",
            body: jsonData,
            requiresAuth: false
        )

        return response.message
    }

    func logout() {
        UserDefaults.standard.removeObject(forKey: "authToken")
    }

    func updateUserProfile(updatedFields: [String: Any]) async throws -> User {
        let jsonData = try JSONSerialization.data(withJSONObject: updatedFields)

        let updatedUser: User = try await APIService.shared.request(
            endpoint: "user/update_info",
            method: "PUT",
            body: jsonData
        )

        return updatedUser
    }

    func fetchUserProfile(email: String) async throws -> User {
        let UserInfoRequest = UserInfoRequest(email: email)
        let jsonData = try JSONEncoder().encode(UserInfoRequest)

        guard let token = UserDefaults.standard.string(forKey: "authToken") else {
            throw APIError.unauthorized
        }

        let headers: [String: String] = ["Authorization": "Bearer \(token)"]

        let user: User = try await APIService.shared.request(
            endpoint: "user/info",
            method: "POST",
            body: jsonData
        )

        return user
    }

    func getRecommendations(request: InsuranceRecommendationRequest) async throws -> [InsuranceProduct] {
        let jsonData = try JSONEncoder().encode(request)

        let response: RecommendationResponse = try await APIService.shared.request(
            endpoint: "recommendation/get_recommendations",
            method: "POST",
            body: jsonData
        )

        return response
    }
}
