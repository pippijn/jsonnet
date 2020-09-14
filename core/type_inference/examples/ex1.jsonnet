{ 
    local base = { 
        local b = self.a {
            z: 3
        },
        a: {
            z: null    
        } 
    }, 
    x: base {}, 
    y: base { s: "str" } 
}

