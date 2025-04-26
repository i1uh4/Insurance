import Foundation

struct User: Codable, Equatable {
    var id: Int?
    var user_name: String
    var email: String
    var isVerified: Bool?
    var createdAt: String?
    var firstName: String?
    var lastName: String?
    var age: Int?
    var gender: String?
    var occupation: String?
    var income: Double?
    var maritalStatus: String?
    var hasChildren: Bool?
    var hasVehicle: Bool?
    var hasHome: Bool?
    var hasMedicalConditions: Bool?
    var travelFrequency: String?

    enum CodingKeys: String, CodingKey {
        case id
        case user_name
        case email
        case isVerified = "is_verified"
        case createdAt = "created_at"
        case firstName = "first_name"
        case lastName = "last_name"
        case age
        case gender
        case occupation
        case income
        case maritalStatus = "marital_status"
        case hasChildren = "has_children"
        case hasVehicle = "has_vehicle"
        case hasHome = "has_home"
        case hasMedicalConditions = "has_medical_conditions"
        case travelFrequency = "travel_frequency"
    }

    static func == (lhs: User, rhs: User) -> Bool {
        return lhs.id == rhs.id
    }

    var isProfileComplete: Bool {
        return age != nil &&
               gender != nil &&
               occupation != nil &&
               income != nil &&
               maritalStatus != nil &&
               travelFrequency != nil
    }
}

struct LoginRequest: Codable {
    let email: String
    let password: String
}

struct RegisterRequest: Codable {
    let user_name:       String
    let email:      String
    let password:   String
}

struct RegisterResponse: Codable {
    let code:       Int
    let message:    String
}

struct AuthResponse: Codable {
    let accessToken:    String
    let tokenType:      String
    let user:           User

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
        case user
    }
}

struct UserInfoRequest: Codable {
    let email: String
}
