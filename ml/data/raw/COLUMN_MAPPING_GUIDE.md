# 🔄 **Column Mapping Guide for Your Dataset**

## 📊 **Your Current Dataset Structure**
Based on your dataset image, you have these columns:
- `id`, `gender`, `masterCategory`, `subCategory`, `articleType`, `baseColour`, `season`, `year`, `usage`, `productDisplayName`

## 🎯 **Required ML System Columns**

### **Essential Columns (MUST HAVE):**
```csv
chest_cm,waist_cm,height_cm,weight_kg,size,style,fit
```

### **Optional Columns (RECOMMENDED):**
```csv
age,shoulder_cm,hip_cm,occasion,brand_preference
```

## 🔄 **Step-by-Step Column Transformation**

### **Step 1: Remove Unnecessary Columns**
Delete these columns (they're not needed for ML):
- ❌ `id` - Product ID
- ❌ `masterCategory` - Apparel/Accessories
- ❌ `subCategory` - Topwear/Bottomwear
- ❌ `articleType` - Shirts/Jeans/etc.
- ❌ `baseColour` - Color information
- ❌ `season` - Seasonal data
- ❌ `year` - Year data
- ❌ `productDisplayName` - Product description

### **Step 2: Rename Existing Columns**
- `usage` → `occasion` (rename this column)

### **Step 3: Add Missing Required Columns**
You need to **ADD** these columns with actual measurement data:
- `chest_cm` - Chest circumference in cm
- `waist_cm` - Waist circumference in cm  
- `height_cm` - Height in cm
- `weight_kg` - Weight in kg
- `size` - Clothing size (XS, S, M, L, XL, XXL)
- `style` - Fashion style (casual, formal, streetwear, classic)
- `fit` - Clothing fit (slim, regular, loose)

### **Step 4: Add Optional Columns (if available)**
- `age` - Age in years
- `shoulder_cm` - Shoulder width in cm
- `hip_cm` - Hip circumference in cm
- `brand_preference` - Brand type (premium, budget, streetwear)

## 📝 **Example Transformation**

**BEFORE (Your Current Data):**
```csv
id,gender,masterCategory,subCategory,articleType,baseColour,season,year,usage,productDisplayName
15970,Men,Apparel,Topwear,Shirts,Navy Blue,Fall,2011,Casual,Turtle Check Men Navy Blu
```

**AFTER (Required ML Format):**
```csv
chest_cm,waist_cm,height_cm,weight_kg,age,shoulder_cm,hip_cm,size,style,fit,occasion,brand_preference
95,80,175,70,25,45,95,M,casual,regular,weekend,unisex
```

## ⚠️ **Important Notes**

1. **Measurements Required**: You need actual body measurements (chest, waist, height, weight)
2. **Size Mapping**: Map your clothing sizes to standard sizes (XS, S, M, L, XL, XXL)
3. **Style Categories**: Use consistent style names (casual, formal, streetwear, classic)
4. **Fit Categories**: Use consistent fit names (slim, regular, loose)
5. **Data Types**: All measurements must be numeric, categories must be text

## 🚀 **Next Steps**

1. **Transform your dataset** using the mapping above
2. **Save as CSV** format
3. **Place in**: `ml/data/raw/your_dataset.csv`
4. **Run training**: `python train.py`

## 📞 **Need Help?**

If you don't have body measurement data, you can:
- Use the sample dataset for testing
- Collect measurements from friends/family
- Use fashion industry standard measurements
- Generate synthetic data for demonstration
