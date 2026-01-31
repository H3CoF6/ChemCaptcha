import CryptoJS from 'crypto-js';

// todo  环境变量！！！
const AES_KEY = CryptoJS.enc.Utf8.parse("1234567890987654");

/**
 * AES-CBC 加密 (对应 Python: aes_cbc_encrypt)
 * 逻辑: 生成随机 IV -> 加密 -> 拼接 IV + 密文 -> Base64
 */
export const encryptPayload = (data: object): string => {
    const jsonStr = JSON.stringify(data);
    const iv = CryptoJS.lib.WordArray.random(16);

    const encrypted = CryptoJS.AES.encrypt(jsonStr, AES_KEY, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    });
    
    const combined = iv.clone().concat(encrypted.ciphertext);
    return CryptoJS.enc.Base64.stringify(combined);
};

/**
 * AES-CBC 解密 (对应 Python: aes_cbc_decrypt)
 * 逻辑: Base64解码 -> 提取前16字节为 IV -> 解密
 */
export const decryptPayload = (base64Str: string): any => {
    try {
        const combined = CryptoJS.enc.Base64.parse(base64Str);
        const iv = CryptoJS.lib.WordArray.create(combined.words.slice(0, 4));
        const ciphertext = CryptoJS.lib.WordArray.create(combined.words.slice(4), combined.sigBytes - 16);

        const decrypted = CryptoJS.AES.decrypt(
            { ciphertext: ciphertext } as any,
            AES_KEY,
            {
                iv: iv,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            }
        );

        return JSON.parse(decrypted.toString(CryptoJS.enc.Utf8));
    } catch (e) {
        console.error("Decryption failed", e);
        return null;
    }
};