const fs = require('fs');
const plist = require('plist');

function calculateDaysToExpiry(expiryDate) {
    const today = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return {
        days: diffDays,
        isExpired: diffDays < 0,
        message: diffDays < 0 ? 
            `Profile expired ${Math.abs(diffDays)} days ago` :
            `Profile will expire in ${diffDays} days`
    };
}

function checkDevicePresence(devices, targetUdid) {
    return devices.includes(targetUdid);
}

function extractPlistContent(raw) {
    const start = raw.indexOf(Buffer.from('<?xml'));
    const end = raw.indexOf(Buffer.from('</plist>')) + '</plist>'.length;

    if (start === -1 || end === -1) {
        throw new Error('Could not extract plist content from provisioning profile.');
    }

    return raw.slice(start, end).toString();
}

function parseProvisioningProfile(filePath, targetUdid) {
    try {
        const raw = fs.readFileSync(filePath);
        const plistXML = extractPlistContent(raw);
        const parsed = plist.parse(plistXML);

        const profileInfo = {
            name: parsed.Name,
            expiry: calculateDaysToExpiry(parsed.ExpirationDate),
            devices: parsed.ProvisionedDevices || [],
            deviceStatus: null
        };

        if (targetUdid) {
            profileInfo.deviceStatus = {
                udid: targetUdid,
                isPresent: checkDevicePresence(profileInfo.devices, targetUdid)
            };
        }

        return profileInfo;
    } catch (err) {
        return {
            error: err.message
        };
    }
}

function main() {
    const filePath = process.argv[2];
    const targetUdid = process.argv[3];

    if (!filePath) {
        return {
            error: 'Please provide the path to a .mobileprovision file.',
            usage: 'Usage: node parseProfile.js <profile-path> [device-udid]'
        };
    }

    const result = parseProvisioningProfile(filePath, targetUdid);
    return result;
}

module.exports = {
    parseProvisioningProfile,
    calculateDaysToExpiry,
    checkDevicePresence,
    main
};


if (require.main === module) {
    const result = main();
    
    // Print the results
    if (result.error) {
        console.log(`Error: ${result.error}`);
        if (result.usage) console.log(result.usage);
    } else {
        console.log(`Profile Name: ${result.name}`);
        console.log(result.expiry.message);
        console.log(`Total Devices: ${result.devices.length}`);
        if (result.deviceStatus) {
            console.log(`Device ${result.deviceStatus.udid}: ${
                result.deviceStatus.isPresent ? 'Present' : 'Not present'
            } in this profile.`);
        }
    }
    
    process.exit(result.deviceStatus?.isPresent ? 0 : 1);
}

