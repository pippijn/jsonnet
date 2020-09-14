{ 
    local f(base) = { 
        x: base { 
            a: 3 
        }, 
        y: base { 
            a: "str" 
        } 
    }, 
    res: f({ a: null }) 
}