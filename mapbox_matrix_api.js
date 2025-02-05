import { WA_ZIP_CODE_GPS } from "../wa_zip_gps"

function makeBatch(size, picki, dropi) {
  const picks = WA_ZIP_CODE_GPS.slice(picki, picki + size)
  const drops = WA_ZIP_CODE_GPS.slice(dropi, dropi + size)
  const batch = [...picks, ...drops]
  return batch
}

function formatUrl(batch) {
  const token = "pk.eyJ1IjoiZ2VsdXNvIiwiYSI6ImNscmhjMWRjNTBwNjgyaXFkbzA5MnFrZHMifQ.4xjAQKACdOGNb1fCxzerHg"
  const sources = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].join(';')
  const destinations = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].join(';')
  const locations = batch.map(([zip, lat, lng]) => `${lng},${lat}`).join(";")
  const url = `https://api.mapbox.com/directions-matrix/v1/mapbox/driving/${locations}?sources=${sources}&annotations=distance&destinations=${destinations}&access_token=${token}`
  console.log(url)
  return { batch, url }
}

async function fetchMatrix(batch, url) {
  await fetch(url)
  .then(res => res.json())
  .then(data => {
    console.log(JSON.stringify(data))
    for (let pick = 0; pick < data.distances.length; pick++) {
      for (let drop = 0; drop < data.distances[pick].length; drop++) {
        const distance = data.distances[pick][drop]
        const pickZip = batch[pick][0]
        const dropZip = batch[drop][0]
        console.log(pickZip, dropZip, distance)
      }
    }
  })
}

async function main() {
  const urls = []
  const size = 12
  const skip = 170
  for (let pick = 0; pick < WA_ZIP_CODE_GPS.length; pick += size) {
    console.log('12 row', pick)
    for (let drop = 0; drop < WA_ZIP_CODE_GPS.length; drop += size) {
      const batch = makeBatch(size, pick, drop)
      const batchUrlPair = formatUrl(batch)
      urls.push(batchUrlPair)
    }
  }

  for (let urli = 0; urli < urls.length; urli++) {
    const { batch, url } = urls[urli]
    if (urli > skip) {
      console.log(`fetching ${urli} of ${urls.length}`)
      fetchMatrix(batch, url)
      await new Promise(resolve => setTimeout(resolve, 1000))
    } else {
      console.log(`skipping ${urli} of ${urls.length}`)
    }
  }
}

await main()
console.log('exit')