import SwiftUI

struct RegisterView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @Environment(\.presentationMode) var presentationMode
    
    @State private var username = ""
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var passwordsMatch = true
    
    var body: some View {
        ZStack {
            VStack(spacing: 20) {
                Text("Create Account")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .padding(.bottom, 30)
                
                VStack(spacing: 15) {
                    TextField("Username", text: $username)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                    
                    TextField("Email", text: $email)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                    
                    SecureField("Password", text: $password)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                    
                    SecureField("Confirm Password", text: $confirmPassword)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                        .onChange(of: confirmPassword) { newValue in
                            passwordsMatch = password == newValue || newValue.isEmpty
                        }
                    
                    if !passwordsMatch {
                        Text("Passwords do not match")
                            .foregroundColor(.red)
                            .font(.caption)
                            .padding(.top, 5)
                    }
                }
                
                CustomButton(
                    title: "Register",
                    action: {
                        if password == confirmPassword {
                            authViewModel.register(name: username, email: email, password: password)
                        } else {
                            passwordsMatch = false
                        }
                    },
                    isLoading: authViewModel.isLoading
                )
                .padding(.top, 10)
                .disabled(username.isEmpty || email.isEmpty)
                
                Button(action: {
                    presentationMode.wrappedValue.dismiss()
                }) {
                    Text("Already have an account? Sign In")
                        .foregroundColor(.blue)
                }
                .padding(.top, 20)
                
                Spacer()
            }
            .padding()
            .navigationBarTitle("Register", displayMode: .inline)
            
            if authViewModel.isLoading {
                LoadingView(message: "Creating account...")
            }
        }
        .alert(item: $authViewModel.registerAlert) { alert in
            Alert(
                title: Text(alert.title),
                message: Text(alert.message),
                dismissButton: .default(Text(alert.dismissButton)) {
                    if let action = alert.action {
                        action()
                    }
                }
            )
        }
        
        .onChange(of: authViewModel.navigateToLogin) { navigateToLogin in
            if navigateToLogin {
                presentationMode.wrappedValue.dismiss()
                authViewModel.navigateToLogin = false
            }
        }
    }
}
