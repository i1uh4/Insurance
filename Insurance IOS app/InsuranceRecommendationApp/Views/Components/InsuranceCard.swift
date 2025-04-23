import SwiftUI

struct InsuranceCard: View {
    var insurance: InsuranceProduct
    
    var body: some View {
        VStack(alignment: .leading) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(insurance.productName)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Text(insurance.provider)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    
                    HStack(spacing: 4) {
                        Text("Score:")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Text(String(format: "%.1f", insurance.matchScore * 10))
                            .font(.caption)
                            .fontWeight(.bold)
                            .foregroundColor(.blue)
                        
                        Text("/ 10")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                VStack(alignment: .trailing) {
                    Text("₽\(Int(insurance.estimatedPrice))")
                        .font(.title3)
                        .fontWeight(.bold)
                        .foregroundColor(.blue)
                    
                    Text("per year")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Text(insurance.description)
                .font(.caption)
                .foregroundColor(.secondary)
                .lineLimit(2)
                .padding(.top, 1)
            
            HStack {
                ForEach(insurance.features.prefix(3), id: \.self) { feature in
                    InsuranceFeatureTag(title: feature)
                }
                
                if insurance.features.count > 3 {
                    Text("+\(insurance.features.count - 3)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.vertical, 4)
                        .padding(.horizontal, 8)
                        .background(Color(.systemGray6))
                        .cornerRadius(20)
                }
            }
            .padding(.top, 8)
        }
        .padding(16)
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color(.systemGray5), radius: 4, x: 0, y: 2)
    }
}

struct InsuranceFeatureTag: View {
    var title: String
    
    var body: some View {
        Text(title)
            .font(.caption)
            .foregroundColor(.secondary)
            .padding(.vertical, 4)
            .padding(.horizontal, 8)
            .background(Color(.systemGray6))
            .cornerRadius(20)
    }
}
