export function savedImageType(type) {
    return type == 'corr' || type == 'stats' || type == 'fc-corr';
}

export function getFnameField(fname, field) {
    let val = null;
    fname.split('_').forEach(part => {
        const pp = part.split('-');
        if (pp.length == 2 && pp[0] == field) {
            val = pp[1];
        }
    });
    return val;
}
