type Status = {
    legs: {
        [key: string]: number[]
    }
    battery: {
        percentage: number
        status: string
    }
}

export type { Status }