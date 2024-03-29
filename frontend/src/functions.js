export function savedImageType(type) {
    return type.match(/corr|stats/);
}

export function enc(val) {
    return encodeURIComponent(val);
}

export function getFnameField(fname, field) {
    let val = null;
    fname.split('_').forEach(part => {
        const pp = part.split('-');
        if (pp[0] == field) {
            val = pp.slice(1).join('-');
        }
    });
    return val;
}
