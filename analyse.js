const escomplex = require('escomplex');

let code = '';
process.stdin.setEncoding('utf8');
process.stdin.on('readable', () => {
    let chunk;
    while ((chunk = process.stdin.read())) code += chunk;
});
process.stdin.on('end', () => {
    try {
        const result = escomplex.analyse(code);
        console.log(JSON.stringify(result.functions));
    } catch {
        console.log("[]");
    }
});