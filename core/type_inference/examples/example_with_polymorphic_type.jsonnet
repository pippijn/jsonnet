{ local f(base) = base { y: "str" }, x: f }

// expected type: {x: ({y?: string, ...} -> {y: string, ...})}