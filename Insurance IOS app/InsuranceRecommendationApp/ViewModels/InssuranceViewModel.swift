import Foundation
import Combine

class InsuranceViewModel: ObservableObject {
    @Published var isCheckingRecommendation = false
    @Published var checkRecommendationError: String? = nil
    
    private var cancellables = Set<AnyCancellable>()
    
    func checkRecommendation(productId: Int, userEmail: String) {
        isCheckingRecommendation = true
        
        // Создаем URL для запроса
        guard let url = URL(string: "http://localhost:8000/recommendation/check_recommendation") else {
            isCheckingRecommendation = false
            checkRecommendationError = "Invalid URL"
            return
        }
        
        // Создаем тело запроса
        let requestBody: [String: Any] = [
            "product_id": productId,
            "user_email": userEmail
        ]
        
        // Преобразуем тело запроса в JSON
        guard let jsonData = try? JSONSerialization.data(withJSONObject: requestBody) else {
            isCheckingRecommendation = false
            checkRecommendationError = "Failed to serialize request body"
            return
        }
        
        // Создаем запрос
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.httpBody = jsonData
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Выполняем запрос
        URLSession.shared.dataTaskPublisher(for: request)
            .map { $0.data }
            .receive(on: DispatchQueue.main)
            .sink(receiveCompletion: { [weak self] completion in
                self?.isCheckingRecommendation = false
                
                if case .failure(let error) = completion {
                    self?.checkRecommendationError = error.localizedDescription
                    print("Error checking recommendation: \(error.localizedDescription)")
                }
            }, receiveValue: { [weak self] data in
                self?.isCheckingRecommendation = false
                print("Recommendation check successful")
                // Здесь можно обработать данные ответа, если нужно
            })
            .store(in: &cancellables)
    }
}
