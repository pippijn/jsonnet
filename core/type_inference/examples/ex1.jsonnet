{ 
    local base = { 
        local b = self.a {
            z: 3
        },
        a: {
            z: null    
        } 
    }, 
    x: base {k: 1}, 
    y: base { s: "str" } 
}

