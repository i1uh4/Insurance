import Foundation

enum APIError: Error {
    case invalidURL
    case requestFailed(Error)
    case invalidResponse
    case decodingFailed(Error)
    case unauthorized
    case validationError(String)
    case clientError(String)
    case serverError(String)
    case unknownError(String)
    case emptyFields
    case invalidEmail
}

class APIService {
    static let shared = APIService()
    private let baseURL = Constants.baseURL

    private init() {}

    private func parseErrorMessage(from data: Data) -> String? {
        if let json = try? JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] {

            if let message = json["message"] as? String {
                return message
            }

            if let detail = json["detail"] as? String {
                return detail
            }

            if let detailsArray = json["detail"] as? [[String: Any]] {
                let messages = detailsArray.compactMap { $0["msg"] as? String }
                if !messages.isEmpty {
                    return messages.joined(separator: ", ")
                }
            }
        }

        return String(data: data, encoding: .utf8)
    }


    func getAuthHeaders() -> [String: String] {
        let token = UserDefaults.standard.string(forKey: "authToken") ?? ""
        return [
            "Content-Type": "application/json",
            "Authorization": "Bearer \(token)"
        ]
    }

    func request<T: Decodable>(endpoint: String, method: String = "GET", body: Data? = nil, requiresAuth: Bool = true) async throws -> T {
        guard let url = URL(string: "\(baseURL)/\(endpoint)") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method

        if requiresAuth {
            let headers = getAuthHeaders()
            headers.forEach { request.addValue($0.value, forHTTPHeaderField: $0.key) }
        } else {
            request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        }

        if let body = body {
            request.httpBody = body
        }

        print("Request URL: \(url.absoluteString)")
        print("Request method: \(method)")
        if let body = body, let bodyString = String(data: body, encoding: .utf8) {
            print("Request body: \(bodyString)")
        }

        do {
            let (data, response) = try await URLSession.shared.data(for: request)

            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.invalidResponse
            }

            print("Response status code: \(httpResponse.statusCode)")
            if let responseString = String(data: data, encoding: .utf8) {
                print("Response data: \(responseString)")
            }

            switch httpResponse.statusCode {
            case 200...299:
                do {
                    return try JSONDecoder().decode(T.self, from: data)
                } catch {
                    print("Decoding error: \(error)")
                    throw APIError.decodingFailed(error)
                }
            case 401:
                throw APIError.unauthorized
            case 422:
                do {
                    let errorResponse = try JSONDecoder().decode(APIErrorResponse.self, from: data)
                    let errorMessage = errorResponse.detail.map { $0.msg }.joined(separator: ", ")
                    throw APIError.validationError(errorMessage)
                } catch let decodingError as APIError {
                    throw decodingError
                } catch {
                    throw APIError.validationError("Validation failed: \(String(data: data, encoding: .utf8) ?? "Unknown error")")
                }
            case 400...499:
                let errorMessage = parseErrorMessage(from: data) ?? "Client error"
                throw APIError.clientError(errorMessage)
            case 500...599:
                let errorMessage = parseErrorMessage(from: data) ?? "Server error"
                throw APIError.serverError(errorMessage)
            default:
                let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
                throw APIError.unknownError(errorMessage)
            }
        } catch let error as APIError {
            throw error
        } catch {
            throw APIError.requestFailed(error)
        }
    }
}
