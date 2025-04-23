import SwiftUI

struct CustomButton: View {
    var title: String
    var action: () -> Void
    var isLoading: Bool = false
    var color: Color = .blue
    
    var body: some View {
        Button(action: action) {
            ZStack {
                RoundedRectangle(cornerRadius: 10)
                    .fill(color)
                    .frame(height: 50)
                
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                } else {
                    Text(title)
                        .font(.headline)
                        .foregroundColor(.white)
                }
            }
        }
        .disabled(isLoading)
    }
}
