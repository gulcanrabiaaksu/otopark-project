import React, { useState } from 'react';
import axios from 'axios';

const loadImageBase64 = (file) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = (error) => reject(error);
    });
}


function Home() {
    const [fileData, setFileData] = useState(null);

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        
        if (file) {
            try {
                const base64Image = await loadImageBase64(file);
                setFileData(base64Image);

                // API isteği burada yapılıyor
                axios({
                    method: "POST",
                    url: "https://detect.roboflow.com/car-space-find/2",
                    params: {
                        api_key: "Lqx7R0mEcLUX1DfexisP"
                    },
                    data: base64Image,
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                })
                .then(function(response) {
                    console.log("Başarılı API Yanıtı:", response.data);
                    // Modelin başarısını kontrol etmek için burada işlemler yapabilirsiniz
                })
                .catch(function(error) {
                    console.log("API Hatası:", error.message);
                });
            } catch (error) {
                console.log("Dosya Okuma Hatası:", error.message);
            }
        }
    };

    return (
        <div>
            <input type="file" onChange={handleFileChange} />
            {fileData && (
                <div>
                    <p>Seçilen Resim:</p>
                    <img src={fileData} alt="Seçilen Resim" style={{ maxWidth: '100%' }} />
                    
                </div>
            )}
            <div>
                hello
            </div>
        </div>
    );
}

export default Home;
