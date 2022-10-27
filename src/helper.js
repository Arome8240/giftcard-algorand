import algosdk from "algosdk";
import { Base64 } from "js-base64";

// Convert 32 byte address to readable 58 byte string
export const getAddress = (addr) => {
  if (!addr) return;
  return algosdk.encodeAddress(Base64.toUint8Array(addr));
};
