import Foundation

struct APIErrorResponse: Codable {
    let detail: [APIErrorDetail]
}

struct APIErrorDetail: Codable {
    let loc: [AnyCodable]
    let msg: String
    let type: String
}

struct AnyCodable: Codable {
    let value: Any

    init(_ value: Any) {
        self.value = value
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()

        if let string = try? container.decode(String.self) {
            value = string
        } else if let int = try? container.decode(Int.self) {
            value = int
        } else if let bool = try? container.decode(Bool.self) {
            value = bool
        } else if let double = try? container.decode(Double.self) {
            value = double
        } else if container.decodeNil() {
            value = NSNull()
        } else {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Cannot decode value"
            )
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()

        switch value {
        case let string as String:
            try container.encode(string)
        case let int as Int:
            try container.encode(int)
        case let bool as Bool:
            try container.encode(bool)
        case let double as Double:
            try container.encode(double)
        case is NSNull:
            try container.encodeNil()
        default:
            throw EncodingError.invalidValue(
                value,
                EncodingError.Context(
                    codingPath: container.codingPath,
                    debugDescription: "Cannot encode value"
                )
            )
        }
    }
}

struct AlertItem: Identifiable {
    let id = UUID()
    let title: String
    let message: String
    let dismissButton: String
    var action: (() -> Void)?

    init(title: String, message: String, dismissButton: String = "OK", action: (() -> Void)? = nil) {
        self.title = title
        self.message = message
        self.dismissButton = dismissButton
        self.action = action
    }
}
