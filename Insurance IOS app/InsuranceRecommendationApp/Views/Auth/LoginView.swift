import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @State private var email = ""
    @State private var password = ""
    @State private var showRegister = false
    
    var body: some View {
        NavigationView {
            ZStack {
                VStack(spacing: 20) {
                    Image(systemName: "shield.checkerboard")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 100, height: 100)
                        .foregroundColor(.blue)
                        .padding(.bottom, 20)
                    
                    Text("Insurance Recommendation")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .padding(.bottom, 30)
                    
                    VStack(spacing: 15) {
                        TextField("Email", text: $email)
                            .padding()
                            .background(Color(.systemGray6))
                            .cornerRadius(10)
                            .autocapitalization(.none)
                            .disableAutocorrection(true)
                        
                        SecureField("Password", text: $password)
                            .padding()
                            .background(Color(.systemGray6))
                            .cornerRadius(10)
                    }
                    
                    CustomButton(
                        title: "Login",
                        action: {
                            authViewModel.login(email: email, password: password)
                        },
                        isLoading: authViewModel.isLoading
                    )
                    .padding(.top, 10)
                    .disabled(email.isEmpty)
                    
                    Button(action: {
                        showRegister = true
                    }) {
                        Text("Don't have an account? Sign Up")
                            .foregroundColor(.blue)
                    }
                    .padding(.top, 20)
                    
                    Spacer()
                }
                .padding()
                .navigationBarHidden(true)
                .background(
                    NavigationLink(
                        destination: RegisterView(),
                        isActive: $showRegister,
                        label: { EmptyView() }
                    )
                )
                
                if authViewModel.isLoading {
                    LoadingView(message: "Logging in...")
                }
            }
            .alert(item: $authViewModel.loginAlert) { alert in
                Alert(
                    title: Text(alert.title),
                    message: Text(alert.message),
                    dismissButton: .default(Text(alert.dismissButton))
                )
            }
        }
    }
}
