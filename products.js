const products = [
    {
        title: "GoSriKi Women's Rayon Viscose Anarkali Printed Kurta with Palazzo & Dupatta",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71mX4WATh-L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Clothing & Accessories",
        type: "Bestseller",
        link: "https://www.amazon.in/GoSriKi-Anarkali-Printed-Dupatta-Yellow-GS_XL_Yellow_X-Large/dp/B0DD78S3M2/ref=zg_bs_c_apparel_d_sccl_1/258-6456087-4061756?pd_rd_w=lYh0S&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0DD78S3M2&psc=1&tag=ankit007"
    },
    {
        title: "Jockey 1406 Women's High Coverage Super Combed Cotton Mid Waist Hipster with Concealed Waistband and Stay Fresh Treatment (Pack of 3_Colors & Prints May Vary)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61bMkDF97VL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Clothing & Accessories",
        type: "Bestseller",
        link: "https://www.amazon.in/Jockey-Womens-Hipster-1406_Dark-Assorted_L/dp/B010FMJKFS/ref=zg_bs_c_apparel_d_sccl_2/258-6456087-4061756?pd_rd_w=lYh0S&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B010FMJKFS&psc=1&tag=ankit007"
    },
    {
        title: "Allen Solly Men's Solid Regular Fit Polo",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71eUwDk8z+L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Clothing & Accessories",
        type: "Bestseller",
        link: "https://www.amazon.in/Allen-Solly-Regular-AMKP317G04249_Jet-Black_Large/dp/B06Y2FG6R7/ref=zg_bs_c_apparel_d_sccl_3/258-6456087-4061756?pd_rd_w=lYh0S&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B06Y2FG6R7&psc=1&tag=ankit007"
    },
    {
        title: "GoSriKi Women's Rayon Viscose Straight Bandhej Printed Kurta with Pant & Dupatta",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61r99GrEgcL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Clothing & Accessories",
        type: "Bestseller",
        link: "https://www.amazon.in/GoSriKi-Straight-Printed-Dupatta-Rani-GS_L_Pink_Large/dp/B0DCK648FV/ref=zg_bs_c_apparel_d_sccl_4/258-6456087-4061756?pd_rd_w=lYh0S&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0DCK648FV&psc=1&tag=ankit007"
    },
    {
        title: "SJeware 12 Pairs Solid Cotton Ankle Length Socks for Men & Women, Multicolor, Pack of 12, Free Size",
        image: "https://images-eu.ssl-images-amazon.com/images/I/81TRdxk1wnL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Clothing & Accessories",
        type: "Bestseller",
        link: "https://www.amazon.in/SJEWARE-Pairs-Solid-Ankle-Multicolor/dp/B0BZVZYXV5/ref=zg_bs_c_apparel_d_sccl_5/258-6456087-4061756?pd_rd_w=lYh0S&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0BZVZYXV5&psc=1&tag=ankit007"
    },
    {
        title: "Amazon Brand - Symbol Men's Solid Cotton Rich Polo T Shirt | Collar Tshirts | Half Sleeves | Plain-Regular Fit (Available in Plus Size)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/713n+TxyfCL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Clothing & Accessories",
        type: "Bestseller",
        link: "https://www.amazon.in/Amazon-Brand-Symbol-Polo_SS19PLS2_Fog-Teal_Large/dp/B07MZG27XK/ref=zg_bs_c_apparel_d_sccl_6/258-6456087-4061756?pd_rd_w=lYh0S&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B07MZG27XK&psc=1&tag=ankit007"
    },
    {
        title: "DOCTOR EXTRA SOFT Doctor Ortho Slippers for Women.",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51dMc66bcZL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Shoes & Handbags",
        type: "Bestseller",
        link: "https://www.amazon.in/DOCTOR-EXTRA-SOFT-D-18-Orthopaedic/dp/B09D8CXJ2Q/ref=zg_bs_c_shoes_d_sccl_1/258-6456087-4061756?pd_rd_w=fFFrL&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B09D8CXJ2Q&psc=1&tag=ankit007"
    },
    {
        title: "ASIAN Men's Wonder-13 Sports Running Shoes…",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61utX8kBDlL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Shoes & Handbags",
        type: "Bestseller",
        link: "https://www.amazon.in/ASIAN-Wonder-13-Sports-Running-Shoes/dp/B01N54ZM9W/ref=zg_bs_c_shoes_d_sccl_2/258-6456087-4061756?pd_rd_w=fFFrL&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B01N54ZM9W&psc=1&tag=ankit007"
    },
    {
        title: "AIRSON AL-5 Slipper for Women | Orthopedic, Diabetic, Pregnancy | Soft Doctor Anti-Skid Slipper for Women |Slides, Flip-Flops, Slippers, Chappals | For Ladies and Girls",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61G2KFSrl0L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Shoes & Handbags",
        type: "Bestseller",
        link: "https://www.amazon.in/Orthopedic-Diabetic-Pregnancy-Anti-Skid-Flip-Flops/dp/B0CCYWR1D8/ref=zg_bs_c_shoes_d_sccl_3/258-6456087-4061756?pd_rd_w=fFFrL&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0CCYWR1D8&psc=1&tag=ankit007"
    },
    {
        title: "ASIAN Men's MEXICO-11 Casual Sneaker Shoes with Synthetic Upper Lightweight Comfortable Mid Top Sneaker Shoes for Men's & Boy's",
        image: "https://images-eu.ssl-images-amazon.com/images/I/81R6YbNKOzL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Shoes & Handbags",
        type: "Bestseller",
        link: "https://www.amazon.in/ASIAN-MEXICO-11-Synthetic-Lightweight-Comfortable/dp/B0DBD6L65N/ref=zg_bs_c_shoes_d_sccl_4/258-6456087-4061756?pd_rd_w=fFFrL&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0DBD6L65N&psc=1&tag=ankit007"
    },
    {
        title: "Liberty Boys Gola-schv School Uniform Shoe",
        image: "https://images-eu.ssl-images-amazon.com/images/I/611zKzx9XKL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Shoes & Handbags",
        type: "Bestseller",
        link: "https://www.amazon.in/Liberty-Force-Gola-SCHV-School-Lacing/dp/B0BYVTZH3Y/ref=zg_bs_c_shoes_d_sccl_5/258-6456087-4061756?pd_rd_w=fFFrL&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0BYVTZH3Y&psc=1&tag=ankit007"
    },
    {
        title: "BRUTON Exclusive Trendy Sports Running Shoes | Casual Shoe | Sneakers for Men's & Boy's",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61gKatv2y7L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Shoes & Handbags",
        type: "Bestseller",
        link: "https://www.amazon.in/BRUTON-Exclusive-Trendy-Shoes-Numeric_9/dp/B0BVJ3TCTQ/ref=zg_bs_c_shoes_d_sccl_6/258-6456087-4061756?pd_rd_w=fFFrL&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0BVJ3TCTQ&psc=1&tag=ankit007"
    },
    {
        title: "SUGAR Cosmetics Matte as Hell Lip Crayon | Lasts upto 8hrs | Water Resistent Lipstick for Women | 2.5gm - 07 Viola",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51qXTEGuz2L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Beauty",
        type: "Bestseller",
        link: "https://www.amazon.in/SUGAR-Cosmetics-Matte-Crayon-Lipstick/dp/B09W5GJNJN/ref=zg_bs_c_beauty_d_sccl_1/258-6456087-4061756?pd_rd_w=GPkBF&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B09W5GJNJN&psc=1&tag=ankit007"
    },
    {
        title: "Ghar Soaps Sandalwood & Saffron Magic Soaps For Bath (300 Gms Pack Of 3) | Paraben Free | Chandan & Kesar Bath Soap | Handmade Soaps For Glowing | Skin Brightening Soap For Men & Women",
        image: "https://images-eu.ssl-images-amazon.com/images/I/71A7tvxJXPL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Beauty",
        type: "Bestseller",
        link: "https://www.amazon.in/Sandalwood-Saffron-300-Handmade-Whitening/dp/B09S6M7JQJ/ref=zg_bs_c_beauty_d_sccl_2/258-6456087-4061756?pd_rd_w=GPkBF&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B09S6M7JQJ&psc=1&tag=ankit007"
    },
    {
        title: "The Derma Co 1% Hyaluronic Sunscreen Aqua Gel SPF 50 PA++++ I For Oily, Dry, Acne-prone Skin | Ultra Lightweight Texture I Non-Greasy I No White Cast | Broad Spectrum Protection & Blue Light Protection | For Men & Women | 30 g",
        image: "https://images-eu.ssl-images-amazon.com/images/I/41v1L8K+11L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Beauty",
        type: "Bestseller",
        link: "https://www.amazon.in/Derma-Co-Hyaluronic-Lightweight-white-cast/dp/B0C6M3KHXV/ref=zg_bs_c_beauty_d_sccl_3/258-6456087-4061756?pd_rd_w=GPkBF&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0C6M3KHXV&psc=1&tag=ankit007"
    },
    {
        title: "Cetaphil Paraben, Sulphate-Free Gentle Skin Hydrating Face Wash Cleanser with Niacinamide, Vitamin B5 for Dry to Normal, Sensitive Skin - 125 ml",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51O+J5jnXcL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Beauty",
        type: "Bestseller",
        link: "https://www.amazon.in/Cetaphil-Sulphate-Free-Hydrating-Niacinamide-Sensitive/dp/B01CCGW4OE/ref=zg_bs_c_beauty_d_sccl_4/258-6456087-4061756?pd_rd_w=GPkBF&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B01CCGW4OE&psc=1&tag=ankit007"
    },
    {
        title: "SUGAR Cosmetics Sugar Kohl Of Honour Intense Kajal | Upto 12 Hrs | Smudge Proof & Waterproof Kajal | Matte Finish | Twist Up Kajal Pencil | Paraben Free - 01 Black Out",
        image: "https://images-eu.ssl-images-amazon.com/images/I/713PykK6pML._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Beauty",
        type: "Bestseller",
        link: "https://www.amazon.in/SUGAR-Cosmetics-Honour-Intense-Kajal/dp/B093H9RF9F/ref=zg_bs_c_beauty_d_sccl_5/258-6456087-4061756?pd_rd_w=GPkBF&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B093H9RF9F&psc=1&tag=ankit007"
    },
    {
        title: "Deconstruct 10% Non-irritating Vitamin C Face Serum For Glowing Skin | Highly Stable Vitamin C Face Serum For Women and Men | Beginner Friendly | 10 ml",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51D+Z8KgKuL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Beauty",
        type: "Bestseller",
        link: "https://www.amazon.in/Deconstruct-Non-irritating-Vitamin-Beginner-Friendly/dp/B0DWT2XL34/ref=zg_bs_c_beauty_d_sccl_6/258-6456087-4061756?pd_rd_w=GPkBF&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0DWT2XL34&psc=1&tag=ankit007"
    },
    {
        title: "Oneplus Bullets Z2 Bluetooth Wireless in Ear Earphones with Mic, Bombastic Bass - 12.4 mm Drivers, 10 Mins Charge - 20 Hrs Music, 30 Hrs Battery Life, IP55 Dust and Water Resistant (Magico Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51UhwaQXCpL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Electronics",
        type: "Bestseller",
        link: "https://www.amazon.in/Oneplus-Bluetooth-Wireless-Earphones-Bombastic/dp/B09TVVGXWS/ref=zg_bs_c_electronics_d_sccl_1/258-6456087-4061756?pd_rd_w=h0A0e&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B09TVVGXWS&psc=1&tag=ankit007"
    },
    {
        title: "boAt Bassheads 100 in Ear Wired Earphones with Mic(Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/513ugd16C6L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Electronics",
        type: "Bestseller",
        link: "https://www.amazon.in/boAt-BassHeads-100-Headphones-Black/dp/B071Z8M4KX/ref=zg_bs_c_electronics_d_sccl_2/258-6456087-4061756?pd_rd_w=h0A0e&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B071Z8M4KX&psc=1&tag=ankit007"
    },
    {
        title: "Samsung Original 25W Type-C Travel Adaptor Without Cable, White",
        image: "https://images-eu.ssl-images-amazon.com/images/I/512UVkoMMEL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Electronics",
        type: "Bestseller",
        link: "https://www.amazon.in/Samsung-Original-Type-C-Adaptor-without/dp/B0D2R2MXXJ/ref=zg_bs_c_electronics_d_sccl_3/258-6456087-4061756?pd_rd_w=h0A0e&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0D2R2MXXJ&psc=1&tag=ankit007"
    },
    {
        title: "Apple 20W USB-C Power Adapter (for iPhone, iPad & AirPods)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/21rFLTV3tML._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Electronics",
        type: "Bestseller",
        link: "https://www.amazon.in/Apple-USB-C-Adapter-iPhone-AirPods/dp/B09794YHBS/ref=zg_bs_c_electronics_d_sccl_4/258-6456087-4061756?pd_rd_w=h0A0e&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B09794YHBS&psc=1&tag=ankit007"
    },
    {
        title: "Samsung Galaxy M35 5G (Thunder Grey,6GB RAM,128GB Storage)| Corning Gorilla Glass Victus+| AnTuTu Score 595K+ | Vapour Cooling Chamber | 6000mAh Battery | 120Hz Super AMOLED Display| Without Charger",
        image: "https://images-eu.ssl-images-amazon.com/images/I/8189mzscM6L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Electronics",
        type: "Bestseller",
        link: "https://www.amazon.in/Samsung-Thunder-Storage-Corning-Gorilla/dp/B0D7Z8CJP8/ref=zg_bs_c_electronics_d_sccl_5/258-6456087-4061756?pd_rd_w=h0A0e&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0D7Z8CJP8&psc=1&tag=ankit007"
    },
    {
        title: "boAt Airdopes 311 Pro, 50HRS Battery, Fast Charge, Dual Mics ENx Tech, Transparent LID, Low Latency, IPX4, IWP Tech, v5.3 Bluetooth Earbuds, TWS Ear Buds Wireless Earphones with mic (Active Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/614gbl-O98L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Electronics",
        type: "Bestseller",
        link: "https://www.amazon.in/boAt-Airdopes-311-Pro-Low-Latency/dp/B0CZ3ZPD8B/ref=zg_bs_c_electronics_d_sccl_6/258-6456087-4061756?pd_rd_w=h0A0e&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0CZ3ZPD8B&psc=1&tag=ankit007"
    },
    {
        title: "Certified Refurbished Echo Dot (4th Gen, 2020 release)| Smart speaker with Alexa (White)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/515MX-RX-mL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Amazon Renewed",
        type: "Bestseller",
        link: "https://www.amazon.in/generation-smart-speaker-powerful-Alexa/dp/B084KQ8NNG/ref=zg_bs_c_amazon-renewed_d_sccl_1/258-6456087-4061756?pd_rd_w=Ky0zA&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B084KQ8NNG&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) boAt Rockerz 255 Pro+ Wireless In Ear Earphones with 40 Hours Battery, ASAP Charge, IPX7, Bluetooth Version 5.0, 10mm Drivers and Voice Assistant with mic (Active Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51fvjLL1QwL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Amazon Renewed",
        type: "Bestseller",
        link: "https://www.amazon.in/boAt-Rockerz-255-Pro-Earphones/dp/B09K2Q2WKZ/ref=zg_bs_c_amazon-renewed_d_sccl_2/258-6456087-4061756?pd_rd_w=Ky0zA&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B09K2Q2WKZ&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Dell Optiplex High Performance Desktop Computer (Intel Core i5 3470/ 16 GB RAM/ 1 TB HDD + 256 GB SSD/ Windows 10 Pro/ MS Office/ Intel HD Graphics/ USB/ Ethernet/WiFi), Black",
        image: "https://images-eu.ssl-images-amazon.com/images/I/31HuAqxwBKL._AC_UL225_SR225,160_.jpg",
        price: "₹11,400.00",
        old_price: "N/A",
        category: "Bestsellers in Amazon Renewed",
        type: "Bestseller",
        link: "https://www.amazon.in/Dell-Optiplex-Performance-Computer-Graphics/dp/B09V5HM6QG/ref=zg_bs_c_amazon-renewed_d_sccl_3/258-6456087-4061756?pd_rd_w=Ky0zA&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B09V5HM6QG&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Lenovo Tab M8 2nd Gen Tablet (8-inch, 2GB, 32GB, Wi-Fi + LTE + Calling), Iron Grey",
        image: "https://images-eu.ssl-images-amazon.com/images/I/31ChV1McHLL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Amazon Renewed",
        type: "Bestseller",
        link: "https://www.amazon.in/Refurbished-Lenovo-M8-2nd-Gen/dp/B097TFRGGM/ref=zg_bs_c_amazon-renewed_d_sccl_4/258-6456087-4061756?pd_rd_w=Ky0zA&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B097TFRGGM&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Lenovo ThinkPad 8th Gen Intel Core i5 Thin & Light HD Laptop (16 GB DDR4 RAM/512 GB SSD/14 (35.6 cm) HD/Windows 11/MS Office/WiFi/Bluetooth 4.1/Webcam/Intel Graphics)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/611AaVzaCQL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Amazon Renewed",
        type: "Bestseller",
        link: "https://www.amazon.in/Refurbished-Lenovo-ThinkPad-Bluetooth-Graphics/dp/B0DMTPY8PJ/ref=zg_bs_c_amazon-renewed_d_sccl_5/258-6456087-4061756?pd_rd_w=Ky0zA&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0DMTPY8PJ&psc=1&tag=ankit007"
    },
    {
        title: "(Refurbished) Boya BYM1 Omnidirectional Lavalier Condenser Microphone with 20ft Audio Cable (Black)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61zICp6Ns0L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Amazon Renewed",
        type: "Bestseller",
        link: "https://www.amazon.in/Boya-Omnidirectional-Lavalier-Condenser-Microphone/dp/B07QWDTND8/ref=zg_bs_c_amazon-renewed_d_sccl_6/258-6456087-4061756?pd_rd_w=Ky0zA&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B07QWDTND8&psc=1&tag=ankit007"
    },
    {
        title: "Casio Vintage A-158WA-1Q Digital Grey Dial Unisex Watch Silver Metal Strap (D011)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61ybeKQto8L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Watches",
        type: "Bestseller",
        link: "https://www.amazon.in/Casio-Vintage-Digital-Grey-Watch-A158WA-1Q/dp/B000GAYQJ0/ref=zg_bs_c_watches_d_sccl_1/258-6456087-4061756?pd_rd_w=1JAD6&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B000GAYQJ0&psc=1&tag=ankit007"
    },
    {
        title: "Casio Youth Series Digital Black Dial Unisex Watch - F-91W-1Q(D002)",
        image: "https://images-eu.ssl-images-amazon.com/images/I/51oNy5CTCOL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Watches",
        type: "Bestseller",
        link: "https://www.amazon.in/Casio-Vintage-Digital-Black-Watch/dp/B00HFPIIOI/ref=zg_bs_c_watches_d_sccl_2/258-6456087-4061756?pd_rd_w=1JAD6&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B00HFPIIOI&psc=1&tag=ankit007"
    },
    {
        title: "Matrix Antique 2.0 Day & Date Softest Silicone Strap Analog Watch for Men & Boys",
        image: "https://images-eu.ssl-images-amazon.com/images/I/711NXCmUfbL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Watches",
        type: "Bestseller",
        link: "https://www.amazon.in/Matrix-Antique-Softest-Silicone-Analog/dp/B0CK6N9VDC/ref=zg_bs_c_watches_d_sccl_3/258-6456087-4061756?pd_rd_w=1JAD6&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0CK6N9VDC&psc=1&tag=ankit007"
    },
    {
        title: "TIMEWEAR Analog Day Date Functioning Stainless Steel Chain Watch for Men",
        image: "https://images-eu.ssl-images-amazon.com/images/I/81nj6IlZpVL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Watches",
        type: "Bestseller",
        link: "https://www.amazon.in/TIMEWEAR-Functioning-White-Chain-Watch/dp/B07MDGSP8F/ref=zg_bs_c_watches_d_sccl_4/258-6456087-4061756?pd_rd_w=1JAD6&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B07MDGSP8F&psc=1&tag=ankit007"
    },
    {
        title: "SPIKY Analog Watch for Kids | 3D Cartoon | 7 Multicolor LED Luminous Lights with Silicone Strap | Unisex Best Birthday Gift | Analogue Wrist Watches for Boys & Girls | Age 3-10 yrs",
        image: "https://images-eu.ssl-images-amazon.com/images/I/41zhQvD8-0L._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Watches",
        type: "Bestseller",
        link: "https://www.amazon.in/SPIKY-Digital-Resistance-Comfortable-Silicone/dp/B09TZW89JV/ref=zg_bs_c_watches_d_sccl_5/258-6456087-4061756?pd_rd_w=1JAD6&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B09TZW89JV&psc=1&tag=ankit007"
    },
    {
        title: "Acnos 6 Colours Luminous LED Display Fashionable Children Kids Digital Watches Waterproof Sports Square Electronic Led Watch for Kids Boy Baby Girls Digital Watch for Kids",
        image: "https://images-eu.ssl-images-amazon.com/images/I/61LS7XrAbmL._AC_UL225_SR225,160_.jpg",
        price: "N/A",
        old_price: "N/A",
        category: "Bestsellers in Watches",
        type: "Bestseller",
        link: "https://www.amazon.in/Luminous-Fashionable-Children-Waterproof-Electronic/dp/B0CBN6CHV1/ref=zg_bs_c_watches_d_sccl_6/258-6456087-4061756?pd_rd_w=1JAD6&content-id=amzn1.sym.cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_p=cde02f8b-0594-439d-9e93-f4cced7ce3ce&pf_rd_r=Y6VNBETBDHB521TYSY9T&pd_rd_wg=IDvur&pd_rd_r=e74aa3dd-6451-4b27-91f1-cf40ecdc4d99&pd_rd_i=B0CBN6CHV1&psc=1&tag=ankit007"
    },
];
