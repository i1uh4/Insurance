import Foundation

struct Insurance: Identifiable, Codable, Equatable {
    var id: Int
    var name: String
    var description: String
    var price: Double
    var company: String
    var category: String
    var coverageAmount: Double
    var duration: Int
    var imageUrl: String?
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case description
        case price
        case company
        case category
        case coverageAmount = "coverage_amount"
        case duration
        case imageUrl = "image_url"
    }
    
    static func == (lhs: Insurance, rhs: Insurance) -> Bool {
        return lhs.id == rhs.id
    }
}

struct InsuranceCategory: Identifiable {
    var id = UUID()
    var name: String
    var icon: String
}

let insuranceCategories = [
    InsuranceCategory(name: "Health", icon: "heart.fill"),
    InsuranceCategory(name: "Life", icon: "person.fill"),
    InsuranceCategory(name: "Auto", icon: "car.fill"),
    InsuranceCategory(name: "Home", icon: "house.fill"),
    InsuranceCategory(name: "Travel", icon: "airplane")
]
