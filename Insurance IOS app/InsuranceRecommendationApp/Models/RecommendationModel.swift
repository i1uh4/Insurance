import Foundation

struct InsuranceRecommendationRequest: Codable {
    var age: Int
    var gender: String
    var occupation: String
    var income: Double
    var maritalStatus: String
    var hasChildren: Bool
    var hasVehicle: Bool
    var hasHome: Bool
    var hasMedicalConditions: Bool
    var travelFrequency: String
    
    enum CodingKeys: String, CodingKey {
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
}

struct InsuranceRecommendationResponse: Codable {
    let recommendations: [Insurance]
}


struct RecommendationRequest: Codable {
    var age: Int
    var gender: String
    var occupation: String
    var income: Double
    var maritalStatus: String
    var hasChildren: Bool
    var hasVehicle: Bool
    var hasHome: Bool
    var hasMedicalConditions: Bool
    var travelFrequency: String
    
    enum CodingKeys: String, CodingKey {
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
}

struct InsuranceProduct: Codable {
    var productId: String
    var productName: String
    var provider: String
    var category: String
    var description: String
    var estimatedPrice: Double
    var matchScore: Double
    var features: [String]
    var suitableFor: [String]
    var risksCovered: [String]
    var recommendationReason: String
    
    enum CodingKeys: String, CodingKey {
        case productId = "product_id"
        case productName = "product_name"
        case provider
        case category
        case description
        case estimatedPrice = "estimated_price"
        case matchScore = "match_score"
        case features
        case suitableFor = "suitable_for"
        case risksCovered = "risks_covered"
        case recommendationReason = "recommendation_reason"
    }
}

typealias RecommendationResponse = [InsuranceProduct]
